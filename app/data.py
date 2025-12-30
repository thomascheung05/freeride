import time
import pandas as pd 
import numpy as np  
import geopandas as gpd 
from shapely.geometry import Point, LineString 
from pathlib import Path 
import xml.etree.ElementTree as ET 
import requests 
import math 
from PIL import Image 
from io import BytesIO 
import csv 
import os 
import win32gui, win32ui, ctypes 
from PIL import Image 
import pyautogui 
import pytesseract                      
APP_FOLDER_PATH = Path(__file__).parent
STATIC_FOLDER_PATH = APP_FOLDER_PATH.parent / 'static'
USER_SAVE_FOLDER_PATH = APP_FOLDER_PATH.parent / 'usersaves'
USER_CONFIG_FOLDER_PATH = USER_SAVE_FOLDER_PATH / 'config'
USER_RIDES_FOLDER_PATH = USER_SAVE_FOLDER_PATH / 'rides'
USER_UNPROCESSED_ROUTES_FOLDER_PATH = USER_SAVE_FOLDER_PATH / 'routes' / 'unprocessed'
USER_PROCESSED_ROUTES_FOLDER_PATH = USER_SAVE_FOLDER_PATH / 'routes' / 'processed'
def distance_m(lat1, lon1, lat2, lon2):
    ########################################################
    # Calculates distance using 2 coordinates
    ######################################################## 
    R = 6371000  
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def save_csv(data, output_csv):
    ########################################################
    # Saves a CSV
    ########################################################     
    df = pd.DataFrame(data, columns=["timestamp", "distance"])
    df.to_csv(output_csv, index=False)
    print(f"Saved data to: {output_csv}")

def compute_heading(lat1, lon1, lat2, lon2):
    ########################################################
    # Computes a heading using 2 coordinates
    ######################################################## 
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    x = math.sin(dLon) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
    heading = math.degrees(math.atan2(x, y))
    return (heading + 360) % 360




#  $$$$$$\                                      $$\ $$\                                $$\ 
# $$  __$$\                                    $$  |$$ |                               $$ |
# $$ /  \__| $$$$$$\ $$\    $$\  $$$$$$\      $$  / $$ |      $$$$$$\   $$$$$$\   $$$$$$$ |
# \$$$$$$\   \____$$\\$$\  $$  |$$  __$$\    $$  /  $$ |     $$  __$$\  \____$$\ $$  __$$ |
#  \____$$\  $$$$$$$ |\$$\$$  / $$$$$$$$ |  $$  /   $$ |     $$ /  $$ | $$$$$$$ |$$ /  $$ |
# $$\   $$ |$$  __$$ | \$$$  /  $$   ____| $$  /    $$ |     $$ |  $$ |$$  __$$ |$$ |  $$ |
# \$$$$$$  |\$$$$$$$ |  \$  /   \$$$$$$$\ $$  /     $$$$$$$$\\$$$$$$  |\$$$$$$$ |\$$$$$$$ |
#  \______/  \_______|   \_/     \_______|\__/      \________|\______/  \_______| \_______|                                                                         
#  $$$$$$\                       $$$$$$\  $$\                                              
# $$  __$$\                     $$  __$$\ \__|                                             
# $$ /  \__| $$$$$$\  $$$$$$$\  $$ /  \__|$$\  $$$$$$\                                     
# $$ |      $$  __$$\ $$  __$$\ $$$$\     $$ |$$  __$$\                                    
# $$ |      $$ /  $$ |$$ |  $$ |$$  _|    $$ |$$ /  $$ |                                   
# $$ |  $$\ $$ |  $$ |$$ |  $$ |$$ |      $$ |$$ |  $$ |                                   
# \$$$$$$  |\$$$$$$  |$$ |  $$ |$$ |      $$ |\$$$$$$$ |                                   
#  \______/  \______/ \__|  \__|\__|      \__| \____$$ |                                   
#                                             $$\   $$ |                                   
#                                             \$$$$$$  |                                   
#                                              \______/                                                                                          
def save_config_preset(preset_name, distbbox, speedbbox, window_name):
    PRESET_SAVE_PATH = USER_CONFIG_FOLDER_PATH / f'{preset_name}.csv'
    
    if os.path.exists(PRESET_SAVE_PATH):
        raise FileExistsError(f"Preset '{preset_name}' already exists at {PRESET_SAVE_PATH}")           #  If preset file already exists we get error

    with open(PRESET_SAVE_PATH, mode='w', newline='', encoding='utf-8') as f:                           # Create new file and write data
        writer = csv.writer(f)
        writer.writerow(["preset_name", "distbbox", "speedbbox", "window_name"])                        # Always write header (new file)
        writer.writerow([preset_name, distbbox, speedbbox, window_name])                                # Write preset values

    print(f"Preset '{preset_name}' created at {PRESET_SAVE_PATH}")

    return PRESET_SAVE_PATH


def load_config_preset(preset_name):
    
    PRESET_SAVE_PATH = USER_CONFIG_FOLDER_PATH / f'{preset_name}.csv'

    with open(PRESET_SAVE_PATH, mode='r', encoding='utf-8') as f:

        reader = csv.DictReader(f)

        for row in reader:# Read the first (and only) row
            
            distbbox = tuple(map(int, row["distbbox"].strip("()").split(",")))# Convert bbox strings "10,20,30,40" → tuple of ints
            speedbbox = tuple(map(int, row["speedbbox"].strip("()").split(",")))
            window_name = row["window_name"]

            return {
                "preset_name": preset_name,
                "distbbox": distbbox,
                "speedbbox": speedbbox,
                "window_name": window_name
            }

    raise ValueError(f"Preset '{preset_name}' is empty.")








# $$$$$$$\                        $$\                                                                     
# $$  __$$\                       $$ |                                                                    
# $$ |  $$ | $$$$$$\  $$\   $$\ $$$$$$\    $$$$$$\                                                        
# $$$$$$$  |$$  __$$\ $$ |  $$ |\_$$  _|  $$  __$$\                                                       
# $$  __$$< $$ /  $$ |$$ |  $$ |  $$ |    $$$$$$$$ |                                                      
# $$ |  $$ |$$ |  $$ |$$ |  $$ |  $$ |$$\ $$   ____|                                                      
# $$ |  $$ |\$$$$$$  |\$$$$$$  |  \$$$$  |\$$$$$$$\                                                       
# \__|  \__| \______/  \______/    \____/  \_______|                                                                                                                                               
# $$\                                $$\ $$\                                                              
# $$ |                               $$ |\__|                             $$\                             
# $$ |      $$$$$$\   $$$$$$\   $$$$$$$ |$$\ $$$$$$$\   $$$$$$\           $$ |                            
# $$ |     $$  __$$\  \____$$\ $$  __$$ |$$ |$$  __$$\ $$  __$$\       $$$$$$$$\                          
# $$ |     $$ /  $$ | $$$$$$$ |$$ /  $$ |$$ |$$ |  $$ |$$ /  $$ |      \__$$  __|                         
# $$ |     $$ |  $$ |$$  __$$ |$$ |  $$ |$$ |$$ |  $$ |$$ |  $$ |         $$ |                            
# $$$$$$$$\\$$$$$$  |\$$$$$$$ |\$$$$$$$ |$$ |$$ |  $$ |\$$$$$$$ |         \__|                            
# \________|\______/  \_______| \_______|\__|\__|  \__| \____$$ |                                         
#                                                      $$\   $$ |                                         
#                                                      \$$$$$$  |                                         
#                                                       \______/                                          
# $$$$$$$\                                                                        $$\                     
# $$  __$$\                                                                       \__|                    
# $$ |  $$ | $$$$$$\   $$$$$$\   $$$$$$$\  $$$$$$\   $$$$$$$\  $$$$$$$\  $$$$$$$\ $$\ $$$$$$$\   $$$$$$\  
# $$$$$$$  |$$  __$$\ $$  __$$\ $$  _____|$$  __$$\ $$  _____|$$  _____|$$  _____|$$ |$$  __$$\ $$  __$$\ 
# $$  ____/ $$ |  \__|$$ /  $$ |$$ /      $$$$$$$$ |\$$$$$$\  \$$$$$$\  \$$$$$$\  $$ |$$ |  $$ |$$ /  $$ |
# $$ |      $$ |      $$ |  $$ |$$ |      $$   ____| \____$$\  \____$$\  \____$$\ $$ |$$ |  $$ |$$ |  $$ |
# $$ |      $$ |      \$$$$$$  |\$$$$$$$\ \$$$$$$$\ $$$$$$$  |$$$$$$$  |$$$$$$$  |$$ |$$ |  $$ |\$$$$$$$ |
# \__|      \__|       \______/  \_______| \_______|\_______/ \_______/ \_______/ \__|\__|  \__| \____$$ |
#                                                                                               $$\   $$ |
#                                                                                               \$$$$$$  |
#                                                                                                \______/ 
def load_in_processed_route(route_name):
    ########################################################
    # Loading in the processed route
    ########################################################

    processed_file_path = USER_PROCESSED_ROUTES_FOLDER_PATH / f'{route_name}.parquet'
    gdf = gpd.read_parquet(processed_file_path)

    return gdf



def convert_gdf_to_lines(gdf):
    ########################################################
    # Converting GDF do a line polygon
    ########################################################

    line = LineString(gdf.geometry.tolist())

    route_line_gdf = gpd.GeoDataFrame(# Make a new GeoDataFrame with just the LineString
        {"geometry": [line]},
        crs=gdf.crs
    )

    return route_line_gdf



def load_in_gpx(route_name):
    ########################################################
    # Load in GPX route to become GDF
    ######################################################## 
        
    gpx_path = USER_UNPROCESSED_ROUTES_FOLDER_PATH / f'{route_name}.gpx'
    tree = ET.parse(gpx_path)
    root = tree.getroot()
    ns = {"g": "http://www.topografix.com/GPX/1/1"}
    
    coords = []

    for pt in root.findall(".//g:trkpt", ns):
        lat = float(pt.attrib["lat"])
        lon = float(pt.attrib["lon"])
        coords.append((lon, lat)) 

    route = gpd.GeoDataFrame(
        {"geometry": [Point(x, y) for x, y in coords]},
        crs="EPSG:4326"
    )

    return route


def densify_route(gdf):
    new_points = []

    for i in range(len(gdf) - 1):
        p1 = gdf.geometry.iloc[i]
        p2 = gdf.geometry.iloc[i + 1]

        # Original point
        new_points.append(p1)

        # Midpoint
        mid = Point(
            (p1.x + p2.x) / 2,
            (p1.y + p2.y) / 2
        )
        new_points.append(mid)

    # Add last point
    new_points.append(gdf.geometry.iloc[-1])

    return gpd.GeoDataFrame(geometry=new_points, crs=gdf.crs)


def add_heading_to_route(route):
    ########################################################
    # Each row gets a heading for google image orientation
    ########################################################     
    gdf = route
    lats = gdf.geometry.y.values
    lons = gdf.geometry.x.values

    headings = []

    for i in range(len(gdf)):
        if i < len(gdf) - 1:
            h = compute_heading(lats[i], lons[i], lats[i+1], lons[i+1]) # heading to next point
        else:
            h = headings[-1] if headings else 0 # last point: repeat previous heading
        headings.append(h)

    gdf["heading"] = headings
    return gdf



def add_cumdist_to_route(route):
    ########################################################
    # Each row gets a cumulative distance along the route value
    ########################################################      
    gdf = route

    mean_lon = gdf.geometry.x.mean()
    utm_zone = int((mean_lon + 180) / 6) + 1
    utm_crs = f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs"
    gdf_m = gdf.to_crs(utm_crs)

    coords = np.array([[p.x, p.y] for p in gdf_m.geometry])

    segment_distances = np.sqrt(np.sum(np.diff(coords, axis=0)**2, axis=1))
    segment_distances = np.insert(segment_distances, 0, 0)
    cumulative_distance = np.cumsum(segment_distances)

    gdf["distance_along_m"] = cumulative_distance   # Add back to original GeoDataFrame

    return gdf



def process_gpx_route(route_name):
    ########################################################
    # Takes in GPX, does all processing required to run in FreeRide, saves as parquet
    ######################################################## 
    route = load_in_gpx(route_name)
    route = densify_route(route)
    route = add_cumdist_to_route(route)
    route = add_heading_to_route(route)
    processed_file_path = USER_PROCESSED_ROUTES_FOLDER_PATH / f'{route_name}.parquet'
    route.to_parquet(processed_file_path, engine='pyarrow', index=False)  
    route.to_csv('route.csv', index=False)












# $$$$$$$$\                            $$$$$$$\  $$\       $$\           
# $$  _____|                           $$  __$$\ \__|      $$ |          
# $$ |    $$$$$$\   $$$$$$\   $$$$$$\  $$ |  $$ |$$\  $$$$$$$ | $$$$$$\  
# $$$$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$$$$$$  |$$ |$$  __$$ |$$  __$$\ 
# $$  __|$$ |  \__|$$$$$$$$ |$$$$$$$$ |$$  __$$< $$ |$$ /  $$ |$$$$$$$$ |
# $$ |   $$ |      $$   ____|$$   ____|$$ |  $$ |$$ |$$ |  $$ |$$   ____|
# $$ |   $$ |      \$$$$$$$\ \$$$$$$$\ $$ |  $$ |$$ |\$$$$$$$ |\$$$$$$$\ 
# \__|   \__|       \_______| \_______|\__|  \__|\__| \_______| \_______|
                                                                       
                                                                       
                                                                       
# $$$$$$$\                                                               
# $$  __$$\                                                              
# $$ |  $$ |$$\   $$\ $$$$$$$\                                           
# $$$$$$$  |$$ |  $$ |$$  __$$\                                          
# $$  __$$< $$ |  $$ |$$ |  $$ |                                         
# $$ |  $$ |$$ |  $$ |$$ |  $$ |                                         
# $$ |  $$ |\$$$$$$  |$$ |  $$ |                                         
# \__|  \__| \______/ \__|  \__|                                         

def get_cord_from_dist_along_route(route, latest_distance):
    ########################################################
    # Inputs route and a distance, Checks all rows for the row with the closest cumdist to latest_distance
    ######################################################## 
    gdf = route
    idx = (gdf["distance_along_m"] - latest_distance).abs().idxmin()

    return gdf.iloc[idx]



def get_streetview_image_from_coord(coord_row, fov=90, pitch=0, size="640x640"):
    ########################################################
    # Pulls a streetview image using a coordinate
    ########################################################     
    row = coord_row
    lat = row.geometry.y
    lon = row.geometry.x
    heading = row.get("heading", 0) 

    with open("googleapikey.txt", "r") as f:
        GOOGLE_API_KEY = f.read().strip()

    url = (
        "https://maps.googleapis.com/maps/api/streetview"
        f"?size={size}"
        f"&location={lat},{lon}"
        f"&fov={fov}"
        f"&heading={heading}"
        f"&pitch={pitch}"
        f"&key={GOOGLE_API_KEY}"
    )

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    
    img_bytes = BytesIO()# Convert image to bytes for sending directly
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes












#  $$$$$$\                                                 $$$$$$\                      
# $$  __$$\                                               $$  __$$\                     
# $$ /  \__| $$$$$$$\  $$$$$$\   $$$$$$\  $$$$$$$\        $$ /  \__| $$$$$$\   $$$$$$\  
# \$$$$$$\  $$  _____|$$  __$$\ $$  __$$\ $$  __$$\       $$ |       \____$$\ $$  __$$\ 
#  \____$$\ $$ /      $$$$$$$$ |$$$$$$$$ |$$ |  $$ |      $$ |       $$$$$$$ |$$ /  $$ |
# $$\   $$ |$$ |      $$   ____|$$   ____|$$ |  $$ |      $$ |  $$\ $$  __$$ |$$ |  $$ |
# \$$$$$$  |\$$$$$$$\ \$$$$$$$\ \$$$$$$$\ $$ |  $$ |      \$$$$$$  |\$$$$$$$ |$$$$$$$  |
#  \______/  \_______| \_______| \_______|\__|  \__|       \______/  \_______|$$  ____/ 
#                                                                             $$ |      
#                                                                             $$ |      
#                                                                             \__|      
# $$$$$$$\             $$\                                                              
# $$  __$$\            $$ |                                                             
# $$ |  $$ | $$$$$$\ $$$$$$\    $$$$$$\                                                 
# $$ |  $$ | \____$$\\_$$  _|   \____$$\                                                
# $$ |  $$ | $$$$$$$ | $$ |     $$$$$$$ |                                               
# $$ |  $$ |$$  __$$ | $$ |$$\ $$  __$$ |                                               
# $$$$$$$  |\$$$$$$$ | \$$$$  |\$$$$$$$ |                                               
# \_______/  \_______|  \____/  \_______|                                               
                                                                                      
                                                                                      
                                                                                      
def list_visible_windows():
    def enum_windows(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and "default" not in title.lower():  # skip empty or "default" titles
                results.append((hwnd, title))

    windows = []
    win32gui.EnumWindows(enum_windows, windows)

    if not windows:
        print("No visible windows found (excluding 'default').")
    else:
        for hwnd, title in windows:
            print(f"HWND: {hwnd}, Title: {title}")
    return windows





def get_window_relative_bbox(window_title):
    # Find the window
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print("Window not found!")
        return None, None 

    # Get client area top-left in screen coordinates
    client_left, client_top = win32gui.ClientToScreen(hwnd, (0, 0))
    print(f"Window client area top-left on screen: {client_left}, {client_top}")

    # Let user click top-left and bottom-right
    print("Move your mouse to the TOP-LEFT corner of the number and wait 3 seconds...")
    time.sleep(3)
    abs_left, abs_top = pyautogui.position()
    print(f"Top-left clicked: {abs_left}, {abs_top}")

    print("Move your mouse to the BOTTOM-RIGHT corner of the number and wait 3 seconds...")
    time.sleep(3)
    abs_right, abs_bottom = pyautogui.position()
    print(f"Bottom-right clicked: {abs_right}, {abs_bottom}")

    # Convert absolute screen coordinates to window-relative coordinates
    rel_left = abs_left - client_left
    rel_top = abs_top - client_top
    rel_right = abs_right - client_left
    rel_bottom = abs_bottom - client_top

    bbox = (rel_left, rel_top, rel_right, rel_bottom)
    print(f"Bounding box relative to window: {bbox}")
    screenshot = capture_window_region(window_title, bbox, speed_bbox= None)

    return bbox, screenshot





def capture_window_region(title, dist_bbox, speed_bbox):
    hwnd = win32gui.FindWindow(None, title) # stores the window in this variable
    if not hwnd:
        print("Window not found!")
        return None
    
    left, top, right, bottom = win32gui.GetClientRect(hwnd) # gets the dimensions of the window
    width = right - left
    height = bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd) # Gets the “device context” for the window, basically a pointer to its pixels.
    mfcDC = win32ui.CreateDCFromHandle(hwndDC) # Wraps the DC in a Python object we can work with.
    saveDC = mfcDC.CreateCompatibleDC() # A memory DC that we can copy the window image into.
    bmp = win32ui.CreateBitmap() # We create a blank bitmap the same size as the window.
    bmp.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(bmp) # SelectObject tells saveDC to draw into this bitmap.
    PW_RENDERFULLCONTENT = 0x00000002
    ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), PW_RENDERFULLCONTENT) #PrintWindow is a Windows function that copies the actual window content into a DC. PW_RENDERFULLCONTENT ensures the entire content is rendered, even if the window is partially offscreen. saveDC.GetSafeHdc() gets a handle to our memory DC so Windows knows where to draw.

    bmpinfo = bmp.GetInfo() # gets infor on bitmap like widht and height
    bmpstr = bmp.GetBitmapBits(True)    # Extracts raw pixel data
    img = Image.frombuffer( # converts to pillow image
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )

    
    dist_cropped_img = img.crop(dist_bbox)    # crops the image to only the bounding box
    if speed_bbox != None:
        speed_cropped_img = img.crop(speed_bbox)
        # free up resources 
        win32gui.DeleteObject(bmp.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        return dist_cropped_img, speed_cropped_img
           

    win32gui.DeleteObject(bmp.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return dist_cropped_img





def extract_number_from_image(img):
    tesseract_path = APP_FOLDER_PATH.parent / "Tesseract" / "tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    text = pytesseract.image_to_string(img, config='--psm 7')  # single line
    text = text.strip().replace(',', '')
    try:
        return float(text)
    except ValueError:
        return None
    




def get_data_once(window_title, distbbox, speedbbox, distance_units):

    dist_img, speed_img = capture_window_region(window_title, distbbox, speedbbox)

    distance = extract_number_from_image(dist_img)
    if distance is None:
        distance = np.nan
    else:
        if distance_units == 'km':
            distance = distance * 1000
        if distance_units == 'miles':
            distance = distance * 1609

    if speed_img != None:
        speed = extract_number_from_image(speed_img)
        if speed is None:
            speed = np.nan
        return distance, speed

    return distance














# $$$$$$$\  $$\       $$$$$$$$\          
# $$  __$$\ $$ |      $$  _____|         
# $$ |  $$ |$$ |      $$ |               
# $$$$$$$\ |$$ |      $$$$$\             
# $$  __$$\ $$ |      $$  __|            
# $$ |  $$ |$$ |      $$ |               
# $$$$$$$  |$$$$$$$$\ $$$$$$$$\          
# \_______/ \________|\________|         
                                       
                                       
                                       
# $$$$$$$\             $$\               
# $$  __$$\            $$ |              
# $$ |  $$ | $$$$$$\ $$$$$$\    $$$$$$\  
# $$ |  $$ | \____$$\\_$$  _|   \____$$\ 
# $$ |  $$ | $$$$$$$ | $$ |     $$$$$$$ |
# $$ |  $$ |$$  __$$ | $$ |$$\ $$  __$$ |
# $$$$$$$  |\$$$$$$$ | \$$$$  |\$$$$$$$ |
# \_______/  \_______|  \____/  \_______|
                                       
                                       
                                           
# import asyncio                        
# from bleak import BleakClient         
# import struct  
# DEVICE_ID = "7CA0DD25-9E34-CF6F-3230-683A4A8974CD"          # ID of device
# CHAR_UUID = "00002A63-0000-1000-8000-00805f9b34fb"          # BLE characteristic UUID to subsribe to, 00002A63 is cycling power  
# WHEEL_CIRCUMFERENCE = 2.105                         # Bike wheel circumference
# prev_crank_revs = None
# prev_crank_event_time = None
# prev_wheel_revs = None
# prev_wheel_event_time = None



# def notification_handler(sender, data): # sender is characteristic handle/ID given by bleak, data is the raw bytes we get from the machine
#     global prev_crank_revs, prev_crank_event_time, prev_wheel_revs, prev_wheel_event_time       # it will read and write variables in the global envs 

#     # Convert to bytes for parsing
#     b = bytearray(data)                                         # Convert the data we get from machine into bytearray meaning we can now index the bytes that the machine sends us 
    
#     # Flags (2 bytes)
#     flags = struct.unpack_from("<H", b, 0)[0]                   # Reads the first two bytes as an Unsigned 16-bit integer, a number stored in 16 bit format that is only positive, this value tell us what data is available in the data packet being sent by the machine 

#     # Instantaneous power (2 bytes, signed)
#     power_watts = struct.unpack_from("<h", b, 2)[0]             # Reads the next two bytes as Signed 16-bit integer, a number stored in 16 bit format that is positive or negative, the highest bit is the sign bit  

#     offset = 4                                                  # This is to keep track where we are in the data string from the machine, we used 2 bits for flag and two for power_watts so we are now at 4 
#     accumulated_torque = None                                   # set to none and only fills is the data is present 
#     crank_revs = None
#     last_crank_event_time = None
#     cadence_rpm = None
#     speed_kmh = None

#     # Check for optional fields based on flags
#     # if flags & 0x01:  # Pedal Power Balance present (skip for now)
#     #     pedal_balance = struct.unpack_from("<B", b, offset)[0]
#     #     offset += 1

#     # if flags & 0x02:  # This checks if accumulated torque is present in the data, if yes it unpacks it and moves the offset up 2
#     #     accumulated_torque = struct.unpack_from("<H", b, offset)[0] / 32.0  # Nm
#     #     offset += 2

#     if flags & 0x04:  # This checks if the wheel revolution data is present and if yes it unpacks it and moves the offest by 6
#         wheel_revs, last_wheel_event_time = struct.unpack_from("<LH", b, offset)
#         offset += 6
        
#         # Calculate speed
#         print("-" * 30)
#         print(f'Prev_wheel_revs:{prev_wheel_revs}')
#         print(f'prev_wheel_event_time:{prev_wheel_event_time}')
#         print("-" * 15)
#         print(f'wheel_revs:{wheel_revs}')
#         print(f'last_wheel_event_time:{last_wheel_event_time}')
#         print("-" * 30)
#         print(prev_wheel_revs, prev_wheel_event_time)
#         if prev_wheel_revs is not None and prev_wheel_event_time is not None:
#             delta_revs = wheel_revs - prev_wheel_revs
#             delta_time_sec = (last_wheel_event_time - prev_wheel_event_time) / 1024
#             if delta_time_sec > 0:
#                 speed_m_s = (delta_revs * WHEEL_CIRCUMFERENCE) / delta_time_sec
#                 speed_kmh = speed_m_s * 3.6
#         prev_wheel_revs = wheel_revs
#         prev_wheel_event_time = last_wheel_event_time # i think because last_wheel_event_time is such a mslal time number that it rounds it to seconds and its alays 0 making the speed value error (divide by 0) and causing it not to display, my theory for now

#     if flags & 0x08:  # Crank Revolution Data present
#         crank_revs, last_crank_event_time = struct.unpack_from("<HH", b, offset)
#         offset += 4
#         # Calculate cadence
#         if prev_crank_revs is not None and prev_crank_event_time is not None:
#             delta_revs = crank_revs - prev_crank_revs
#             delta_time_sec = (last_crank_event_time - prev_crank_event_time) / 1024
#             if delta_time_sec > 0:
#                 cadence_rpm = (delta_revs / delta_time_sec) * 60
#         prev_crank_revs = crank_revs
#         prev_crank_event_time = last_crank_event_time

#     # Print all parsed variables
#     # print(f"Flags: {flags}")
#     # print(f"Power (W): {power_watts}")
#     # if accumulated_torque is not None:
#     #     print(f"Torque (Nm): {accumulated_torque}")
#     # if crank_revs is not None:
#     #     print(f"Crank Revs: {crank_revs}")
#     #     print(f"Last Crank Event Time: {last_crank_event_time}")
#     # if cadence_rpm is not None:
#     #     print(f"Cadence (RPM): {cadence_rpm:.2f}")
#     # if wheel_revs is not None:
#     #     print(f"Wheel Revs: {wheel_revs}")
#     #     print(f"Last Wheel Event Time: {last_wheel_event_time}")
#     # if speed_kmh is not None:
#     #     print(f"Speed (km/h): {speed_kmh:.2f}")
#     # print("-" * 30)
    


# async def fx_connect_to_device():
#     print("Trying to connect to KICKR SNAP...")

#     async with BleakClient(DEVICE_ID) as client:
#         if client.is_connected:
#             print("Connected to KICKR SNAP")
#             # Subscribe to notifications
#             await client.start_notify(CHAR_UUID, notification_handler)
#             print("Subscribed to notifications. Waiting for data...")
            
#             # Keep the program running to receive notifications
#             await asyncio.sleep(30)  # Adjust the duration as needed
#             await client.stop_notify(CHAR_UUID)
#         else:
#             print("Failed to connect.")

# # Run the async function
# asyncio.run(fx_connect_to_device())














































































