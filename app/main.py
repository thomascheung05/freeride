import math
from data import ( 
                 load_in_processed_route, 
                 process_gpx_route, 
                 convert_gdf_to_lines,
                 get_cord_from_dist_along_route, 
                 get_streetview_image_from_coord,
                 distance_m,
                 save_config_preset,load_config_preset,
                 get_window_relative_bbox,
                 list_visible_windows,
                 get_data_once)
import csv 
import os 
from flask import Flask, json,request, jsonify 
from pathlib import Path 
from io import BytesIO 
import time 
import base64 
import pandas as pd

CURRENT_CONFIG = {}
APP_FOLDER_PATH = Path(__file__).parent
STATIC_FOLDER_PATH = APP_FOLDER_PATH.parent / 'static'
USER_SAVE_FOLDER_PATH = APP_FOLDER_PATH.parent / 'usersaves'
USER_CONFIG_FOLDER_PATH = USER_SAVE_FOLDER_PATH / 'config'
USER_RIDES_FOLDER_PATH = USER_SAVE_FOLDER_PATH / 'rides'
USER_UNPROCESSED_ROUTES_FOLDER_PATH = USER_SAVE_FOLDER_PATH / 'routes' / 'unprocessed'
USER_PROCESSED_ROUTES_FOLDER_PATH = USER_SAVE_FOLDER_PATH / 'routes' / 'processed'






#############################
# Main Flask 
#############################
app = Flask(__name__, static_folder= STATIC_FOLDER_PATH)
@app.route('/')
def serve_html():
    return app.send_static_file('web.html')










@app.route('/api/get_window', methods=['GET'])
####################################################################################################################
# User Configuration: Show all open windows
####################################################################################################################
def get_window():
    windows = list_visible_windows()
    formatted_windows = "\n".join([f"Title: {title}, HWND: {hwnd}" for hwnd, title in windows])
    return jsonify({"formatted_windows": formatted_windows})










@app.route('/api/get_bbox', methods=['POST'])
####################################################################################################################
# User Configuration: Get bounding box coordinates
####################################################################################################################
def get_bbox():
    data = request.get_json()
    USER_WINDOW_NAME = data.get("window_name", "")
    if not USER_WINDOW_NAME:
        USER_WINDOW_NAME = " No Window Name Inputed"

    bbox, screenshot = get_window_relative_bbox(USER_WINDOW_NAME)
    if bbox is None or screenshot is None:
        return jsonify({
            "status": "error",
            "code": "WINDOW_NOT_FOUND",
            "message": f"Error:{USER_WINDOW_NAME}"
        }), 404     
      
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return jsonify({"bbox": bbox, "screenshot": img_str})










@app.route('/api/process_route', methods=['POST'])
####################################################################################################################
# User Configuration: Process and Save an unprocessed route
####################################################################################################################
def process_route():
    data = request.get_json()

    route_name = data.get("route_to_process")
    
    process_gpx_route(route_name)
    return jsonify({
            "status": "success",
            "message": f"Preset '{route_name}' saved successfully."
        }), 200










@app.route('/api/save_preset', methods=['POST'])
####################################################################################################################
# User Configuration: Save Preset user created
####################################################################################################################
def save_preset():
    data = request.get_json()

    preset_name = data.get("preset_name")
    distbbox = data.get("distbbox")
    speedbbox = data.get("speedbbox")
    window_name = data.get("window_name")
    try:
        save_config_preset(preset_name, distbbox, speedbbox, window_name)

        return jsonify({
            "status": "success",
            "message": f"Preset '{preset_name}' saved successfully."
        }), 200

    except FileExistsError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 409  # conflict error if preset exists

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500










@app.route('/api/freeride_run', methods=['POST'])
####################################################################################################################
# FREERIDE MAIN RUNNER
####################################################################################################################
def freeride_run():
    data = request.get_json()

    preset_name = data["preset_name"]
    route_name = data["route"]
    start_dist = int(data["start_dist"])

    if preset_name == '' and route_name == '':
        print("NO preset or route was selected")
        return jsonify({
            "status": "error",
            "message": "No preset or route selected"
        }), 400
    elif preset_name == '':
        print("NO preset was selected")
        return jsonify({
            "status": "error",
            "message": "NO preset was selected"
        }), 400
    elif route_name == '':
        print("NO route was selected")
        return jsonify({
            "status": "error",
            "message": "NO route was selected"
        }), 400

        

    preset = load_config_preset(preset_name)

    route = load_in_processed_route(route_name)
    route_line = convert_gdf_to_lines(route)
    route_line_geojson = json.loads(route_line.to_json())

    CURRENT_CONFIG["dist_bbox"] = preset["distbbox"]
    CURRENT_CONFIG["speed_bbox"] = preset["speedbbox"]
    CURRENT_CONFIG["window_name"] = preset["window_name"]
    CURRENT_CONFIG["route_name"] = route_name
    CURRENT_CONFIG["last_rec_distance"] = None
    CURRENT_CONFIG["last_distance_along_route"] = None
    CURRENT_CONFIG["start_dist"] = start_dist
    CURRENT_CONFIG["route"] = route
    CURRENT_CONFIG["last_google_image"] = None
    

    return jsonify({
        "status": "ready",
        "route": route_line_geojson 
    })
    









@app.route("/api/get_position", methods=["GET"])
####################################################################################################################
# Get poll position, run every interval
####################################################################################################################
def get_position():
    global CURRENT_CONFIG
    cfg = CURRENT_CONFIG

    latest_distance, latest_speed, window_not_found_flag = get_data_once(cfg["window_name"], cfg["dist_bbox"], cfg["speed_bbox"], 'km')
    
    # Return an error if the window was not found when trying to get the image
    if window_not_found_flag == True:
        return jsonify({
            "status": "error",
            "message": "The capture window was not found"
        }), 400
    print(latest_distance)
    latest_distance = latest_distance + cfg["start_dist"]
    print(latest_distance)
    if pd.isna(latest_distance):
        if cfg['last_rec_distance'] == None:
            latest_distance = 0
        else:
            latest_distance = cfg['last_rec_distance']
    if latest_speed is None or math.isnan(latest_speed):
        latest_speed = 9999999 

    cord_row = get_cord_from_dist_along_route(cfg["route"], latest_distance)

    dist_along_route = cord_row.distance_along_m
    lat = float(cord_row.geometry.y)
    lon = float(cord_row.geometry.x)    

    # Determine if we should pull and display a new image or not
    should_pull_image = False
    if cfg['last_rec_distance'] is None:                # if this is the first time polling position
        should_pull_image = True
        cfg['last_rec_distance'] = latest_distance
        cfg['last_distance_along_route'] = dist_along_route
        distance_traveled = 0
    else:
        distance_traveled = latest_distance - cfg['last_rec_distance']
        if distance_traveled > 25 and cfg['last_distance_along_route'] != dist_along_route:                 # moved more than 15 m
            should_pull_image = True
            cfg['last_rec_distance'] = latest_distance  
            cfg['last_distance_along_route'] = dist_along_route
        else:           # Dont think we need this here actually
            should_pull_image = False
            
    print("="*90)
    print("NEW POSITION RECORDED")
    print("="*90)
    print()
    print(f"{'Recorded Distance:':<20} {latest_distance:.3f}")
    print(f"{'Recorded Speed:':<20} {latest_speed:.3f}")
    print(f"{'Latitude:':<20} {lat:.6f}")
    print(f"{'Longitude:':<20} {lon:.6f}")
    print(f"{'Distance along route:':<20} {dist_along_route:.3f}")
    print(f"{'Heading:':<20} {cord_row.heading:.3f}")
    print()

    latest_steet_img = None
    if should_pull_image:
        print(f'-------> Pulling new StreetView image (moved {distance_traveled}m since last image)')
        
        def encode_image_to_base64(image_io):
            import base64
            if isinstance(image_io, BytesIO):
                return base64.b64encode(image_io.getvalue()).decode("utf-8")
            else:
                with open(image_io, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
        
        latest_steet_img = get_streetview_image_from_coord(cord_row, fov=90, pitch=0, size="600x400")
        latest_steet_img_b64 = encode_image_to_base64(latest_steet_img)
        print("-------> Image Success!")
    else:
        print(f'-------> Skipping image (moved {distance_traveled}m since last image)')
        latest_steet_img_b64 = None 

    print("="*90)    

    return jsonify({
        "distance": latest_distance,
        "speed": latest_speed,
        "image": latest_steet_img_b64,
        "lat": float(cord_row.geometry.y),
        "lon": float(cord_row.geometry.x)
    })










@app.route('/api/freeride_stop', methods=['POST'])
####################################################################################################################
# Stop freeride from running 
####################################################################################################################
def freeride_stop():
    global CURRENT_CONFIG
    cfg = CURRENT_CONFIG
    if CURRENT_CONFIG:
         
        ride_data = {
            "route_name": CURRENT_CONFIG.get("route_name", ""),
            "latest_distance": CURRENT_CONFIG.get("latest_distance", 0),
            "dist_bbox": CURRENT_CONFIG.get("dist_bbox", ""),
            "speed_bbox": CURRENT_CONFIG.get("speed_bbox", ""),
            "window_name": CURRENT_CONFIG.get("window_name", ""),
            "timestamp": time.time()  # optional: record when the ride stopped
        }

         
        SAVE_FILE = USER_RIDES_FOLDER_PATH / 'SAVED_RIDES.csv'
        file_exists = SAVE_FILE.exists()
        with open(SAVE_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=ride_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(ride_data)


    
    CURRENT_CONFIG = {}
    CURRENT_CONFIG['last_rec_distance'] = None
    CURRENT_CONFIG['last_distance_along_route'] = None

    print("="*10)
    print("FREERIDE STOPPED: global variables cleared")
    print("="*10)

    return jsonify({"status": "success", "message": "Freeride stopped, globals cleared."})










@app.route('/api/init_ui', methods=['GET'])
####################################################################################################################
# Initiate the User Interface
####################################################################################################################
def init_ui():
    # Helper to strip extensions
    def strip_ext(file_list):
        return [os.path.splitext(f)[0] for f in file_list]

    # Get unprocessed files
    try:
        unprocessed_files = [
            f for f in os.listdir(USER_UNPROCESSED_ROUTES_FOLDER_PATH)
            if os.path.isfile(os.path.join(USER_UNPROCESSED_ROUTES_FOLDER_PATH, f))
        ]
        unprocessed_files = strip_ext(unprocessed_files)
    except Exception as e:
        unprocessed_files = []
        print("Error reading unprocessed folder:", e)

    # Get processed files
    try:
        processed_files = [
            f for f in os.listdir(USER_PROCESSED_ROUTES_FOLDER_PATH)
            if os.path.isfile(os.path.join(USER_PROCESSED_ROUTES_FOLDER_PATH, f))
        ]
        processed_files = strip_ext(processed_files)
    except Exception as e:
        processed_files = []
        print("Error reading processed folder:", e)

    # Get config presets
    try:
        config_presets = [
            f for f in os.listdir(USER_CONFIG_FOLDER_PATH)
            if os.path.isfile(os.path.join(USER_CONFIG_FOLDER_PATH, f))
        ]
        config_presets = strip_ext(config_presets)
    except Exception as e:
        config_presets = []
        print("Error reading config folder:", e)

    return jsonify({
        "status": "success",
        "unprocessed_files": unprocessed_files,
        "processed_files": processed_files,
        "config_presets": config_presets
    })










if __name__ == '__main__':
    app.run(debug=False)