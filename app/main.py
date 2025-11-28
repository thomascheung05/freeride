from data import log_numbers
from screencapture import get_window_relative_bbox, list_visible_windows

from pathlib import Path

app_folder_path = Path(__file__).parent
screenshots_folder_path = app_folder_path.parent / 'testscreenshots' 

#USER_WINDOW_NAME = "LetsView [Cast]"
USER_WINDOW_NAME = "(513) Turning the cheapest Amazon boat into a stealth camper - YouTube - Google Chrome"
action = "get a bounder box cooddinates"
#action = "find casting window"
#action = "record numbers"

if action == "get a bounder box cooddinates":
    get_window_relative_bbox(USER_WINDOW_NAME,screenshots_folder_path / "testingscreenshots.jpg")
if action == "find casting window":
    list_visible_windows()
if action == "record numbers":
    window_title = "LetsView [Cast]"
    bbox = (9, 379, 183, 449)  # window-relative coordinates
    captureinterval = 5
    totaldistance =2
    log_numbers(window_title, bbox, captureinterval, totaldistance, output_csv="speed_data.csv")







