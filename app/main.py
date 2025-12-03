from data import ( 
                 save_csv,
                 load_in_processed_route, 
                 process_gpx_route, convert_gdf_to_lines,
                 get_cord_from_dist_along_route, 
                 get_streetview_image_from_coord,distance_m,
                 save_config_preset,load_config_preset)
from screencapture import (get_window_relative_bbox, 
                           list_visible_windows,
                           get_data_once)
from flask import Flask, json, render_template, request, jsonify, send_file, Response
from pathlib import Path
from io import BytesIO
import io
import time
import base64
CURRENT_CONFIG = {}
LAST_COORD = None
APP_FOLDER_PATH = Path(__file__).parent
SCREENSHOTS_FOLDER_PATH = APP_FOLDER_PATH.parent / 'testscreenshots'
UNPROCESSED_ROUTES_FOLDER_PATH = APP_FOLDER_PATH.parent / 'routes' / 'unprocessed'
PROCESSED_ROUTES_FOLDER_PATH = APP_FOLDER_PATH.parent / 'routes' / 'processed'
STATIC_FOLDER_PATH = APP_FOLDER_PATH.parent / 'static'
IMAGE_FOLDER_PATH = STATIC_FOLDER_PATH / 'streetviewimages'





app = Flask(__name__, static_folder= STATIC_FOLDER_PATH)

# Serve your main HTML
@app.route('/')
def serve_html():
    return app.send_static_file('web.html')


# Example endpoint for "get_window"
@app.route('/api/get_window', methods=['GET'])
def get_window():
    windows = list_visible_windows()
    formatted_windows = "\n".join([f"Title: {title}, HWND: {hwnd}" for hwnd, title in windows])
    return jsonify({"formatted_windows": formatted_windows})


@app.route('/api/get_bbox', methods=['POST'])
def get_bbox():
    data = request.get_json()
    USER_WINDOW_NAME = data.get("window_name", "")
    if not USER_WINDOW_NAME:
        USER_WINDOW_NAME = "LetsView [Cast]"

    bbox, screenshot = get_window_relative_bbox(USER_WINDOW_NAME)
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return jsonify({"bbox": bbox, "screenshot": img_str})



@app.route('/api/save_preset', methods=['POST'])
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




@app.route('/api/process_route', methods=['POST'])
def process_route():
    data = request.get_json()

    route_name = data.get("route_to_process")
    
    process_gpx_route(route_name)
    return jsonify({
            "status": "success",
            "message": f"Preset '{route_name}' saved successfully."
        }), 200



@app.route('/api/freeride_run', methods=['POST'])
def freeride_run():
    data = request.get_json()

    preset_name = data["preset_name"]
    route_name = data["route"]
    start_dist = data["start_dist"]

    
    preset = load_config_preset(preset_name)

    # Save everything to global memory
    CURRENT_CONFIG["dist_bbox"] = preset["distbbox"]
    CURRENT_CONFIG["speed_bbox"] = preset["speedbbox"]
    CURRENT_CONFIG["window_name"] = preset["window_name"]
    CURRENT_CONFIG["route_name"] = route_name
    CURRENT_CONFIG["latest_distance"] = start_dist
    route = load_in_processed_route(route_name)
    CURRENT_CONFIG["route"] = route
    route_line = convert_gdf_to_lines(route)
    route_line_geojson = json.loads(route_line.to_json())

    return jsonify({
        "status": "ready",
        "route": route_line_geojson 
    })
    

@app.route("/api/get_position", methods=["GET"])
def get_position():
    cfg = CURRENT_CONFIG
    latest_distance, latest_speed = get_data_once(cfg["window_name"], cfg["dist_bbox"], cfg["speed_bbox"], 'km')

    route = cfg["route"]
    cord_row = get_cord_from_dist_along_route(route, latest_distance)
    lat = float(cord_row.geometry.y)
    lon = float(cord_row.geometry.x)

    if latest_speed is None:
        latest_speed = 999


    should_pull_image = False
    global LAST_COORD
    if LAST_COORD is None:
        # First time ever → pull an image
        should_pull_image = True
        LAST_COORD = (lat, lon)

    else:
        prev_lat, prev_lon = LAST_COORD
        d = distance_m(prev_lat, prev_lon, lat, lon)

        if d > 10:                 # moved more than 10 m
            should_pull_image = True
            LAST_COORD = (lat, lon)  # update global stored coordinate
        else:
            should_pull_image = False


    latest_steet_img = None
    if should_pull_image:
        print("Pulling new StreetView image (moved >10 m)")
        
        def encode_image_to_base64(image_io):
            """
            Accepts either a BytesIO object or a file path string.
            Returns base64-encoded string.
            """
            import base64
            if isinstance(image_io, BytesIO):
                return base64.b64encode(image_io.getvalue()).decode("utf-8")
            else:
                with open(image_io, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
        
        latest_steet_img = get_streetview_image_from_coord(cord_row, fov=90, pitch=0, size="600x400")
        latest_steet_img_b64 = encode_image_to_base64(latest_steet_img)
    else:
        print("Skipping image (not moved enough)")
        latest_steet_img_b64 = None  # now it's safely defined

    return jsonify({
        "distance": latest_distance,
        "speed": latest_speed,
        "image": latest_steet_img_b64,
        "lat": float(cord_row.geometry.y),
        "lon": float(cord_row.geometry.x)
    })








if __name__ == '__main__':
    app.run(debug=False)








# app = Flask(__name__, static_folder=STATIC_FOLDER_PATH)
# @app.route('/flask_main', methods=['GET'])

# def flask_main():
    
#     action = request.args.get('action')

#     #action = "get_bounding_box_coordinates"
#     #action = "find_casting_window"
#     # action = "record_numbers"
#     #action = "process_data_file"
#     #action = "get_1_streetview_image"

#     if action == "get_bounding_box_coordinates":
#         USER_WINDOW_NAME = "LetsView [Cast]"
#         get_window_relative_bbox(USER_WINDOW_NAME, SCREENSHOTS_FOLDER_PATH / "testingscreenshots.jpg")
#         jsonify({"status": "success", "message": "Bounding box saved"})
#     if action == "find_casting_window":
#         windows = list_visible_windows()
#         return jsonify({"windows": windows})
#     if action == "record_numbers":
#         USER_WINDOW_NAME = "LetsView [Cast]"
#         bbox = (9, 379, 183, 449)  
#         capture_interval = 5
#         total_distance =2
#         output_csv = "distance_log.csv"
#         data = freeride_loop(USER_WINDOW_NAME, bbox, capture_interval, total_distance)
#         save_csv(data, output_csv)
#     if action == "process_data_file":
#         process_gpx_route('testroute')
#     if action == "get_1_streetview_image":
#         route = load_in_processed_route('testroute')
#         DISTANCE_ALONGE_ROUTE = 200    
#         coord_row = get_cord_from_dist_along_route(route, DISTANCE_ALONGE_ROUTE)
#         img_io  = get_streetview_image_from_coord(coord_row)

#         return send_file(img_io, mimetype='image/png')
#     return jsonify({"status": "success", "message": "Process Succesful"})


# @app.route('/')
# def serve_html():
#     return app.send_static_file('web.html')

# if __name__ == '__main__':
#     app.run(debug=False)














