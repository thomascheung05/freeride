from data import (freeride_loop, 
                 save_csv,
                 load_in_processed_route, 
                 process_gpx_route, 
                 get_cord_from_dist_along_route, 
                 get_streetview_image_from_coord)
from screencapture import (get_window_relative_bbox, 
                           list_visible_windows)
from pathlib import Path
app_folder_path = Path(__file__).parent
screenshots_folder_path = app_folder_path.parent / 'testscreenshots' 
unprocessed_routes_folder_path = app_folder_path.parent / 'routes' / 'unprocessed'
processed_routes_folder_path = app_folder_path.parent / 'routes' / 'processed'




#action = "get a bounder box cooddinates"
#action = "find casting window"
# action = "record numbers"
#action = "process data file"
action = "get 1 streetview image"

if action == "get a bounder box cooddinates":
    USER_WINDOW_NAME = "LetsView [Cast]"
    get_window_relative_bbox(USER_WINDOW_NAME, screenshots_folder_path / "testingscreenshots.jpg")
if action == "find casting window":
    list_visible_windows()
if action == "record numbers":
    USER_WINDOW_NAME = "LetsView [Cast]"
    bbox = (9, 379, 183, 449)  
    capture_interval = 5
    total_distance =2
    output_csv = "distance_log.csv"
    data = freeride_loop(USER_WINDOW_NAME, bbox, capture_interval, total_distance)
    save_csv(data, output_csv)
if action == "process data file":
    route = process_gpx_route('testroute')
if action == "get 1 streetview image":
    route = load_in_processed_route('testroute')
    DISTANCE_ALONGE_ROUTE = 200    
    coord_row = get_cord_from_dist_along_route(route, DISTANCE_ALONGE_ROUTE)
    get_streetview_image_from_coord(coord_row)







