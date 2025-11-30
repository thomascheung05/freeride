from data import (freeride_loop, 
                 save_csv,
                 load_in_processed_route, 
                 process_gpx_route, 
                 get_cord_from_dist_along_route, 
                 get_streetview_image_from_coord)
from screencapture import (get_window_relative_bbox, 
                           list_visible_windows)
from flask import Flask, render_template, request, jsonify, send_file, Response
from pathlib import Path
from io import BytesIO

APP_FOLDER_PATH = Path(__file__).parent
SCREENSHOTS_FOLDER_PATH = APP_FOLDER_PATH.parent / 'testscreenshots'
UNPROCESSED_ROUTES_FOLDER_PATH = APP_FOLDER_PATH.parent / 'routes' / 'unprocessed'
PROCESSED_ROUTES_FOLDER_PATH = APP_FOLDER_PATH.parent / 'routes' / 'processed'
STATIC_FOLDER_PATH = APP_FOLDER_PATH.parent / 'static'
IMAGE_FOLDER_PATH = STATIC_FOLDER_PATH / 'streetviewimages'




app = Flask(__name__, static_folder=STATIC_FOLDER_PATH)
@app.route('/flask_main', methods=['GET'])

def flask_main():
    
    action = request.args.get('action')

    #action = "get_bounding_box_coordinates"
    #action = "find_casting_window"
    # action = "record_numbers"
    #action = "process_data_file"
    #action = "get_1_streetview_image"

    if action == "get_bounding_box_coordinates":
        USER_WINDOW_NAME = "LetsView [Cast]"
        get_window_relative_bbox(USER_WINDOW_NAME, SCREENSHOTS_FOLDER_PATH / "testingscreenshots.jpg")
        jsonify({"status": "success", "message": "Bounding box saved"})
    if action == "find_casting_window":
        windows = list_visible_windows()
        return jsonify({"windows": windows})
    if action == "record_numbers":
        USER_WINDOW_NAME = "LetsView [Cast]"
        bbox = (9, 379, 183, 449)  
        capture_interval = 5
        total_distance =2
        output_csv = "distance_log.csv"
        data = freeride_loop(USER_WINDOW_NAME, bbox, capture_interval, total_distance)
        save_csv(data, output_csv)
    if action == "process_data_file":
        process_gpx_route('testroute')
    if action == "get_1_streetview_image":
        route = load_in_processed_route('testroute')
        DISTANCE_ALONGE_ROUTE = 200    
        coord_row = get_cord_from_dist_along_route(route, DISTANCE_ALONGE_ROUTE)
        img_io  = get_streetview_image_from_coord(coord_row)

        return send_file(img_io, mimetype='image/png')
    return jsonify({"status": "success", "message": "Process Succesful"})


@app.route('/')
def serve_html():
    return app.send_static_file('web.html')

if __name__ == '__main__':
    app.run(debug=False)














