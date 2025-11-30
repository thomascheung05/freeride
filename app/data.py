
import time
import time
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import numpy as np
from pathlib import Path
from screencapture import read_distance_once
import xml.etree.ElementTree as ET
import requests
import math
from PIL import Image
from io import BytesIO
app_folder_path = Path(__file__).parent
screenshots_folder_path = app_folder_path.parent / 'testscreenshots' 
unprocessed_routes_folder_path = app_folder_path.parent / 'routes' / 'unprocessed'
processed_routes_folder_path = app_folder_path.parent / 'routes' / 'processed'





def load_in_gpx(route_name):
    gpx_path = unprocessed_routes_folder_path / f'{route_name}.gpx'
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





def load_in_processed_route(route_name):
    processed_file_path = processed_routes_folder_path / f'{route_name}.parquet'

    gdf = gpd.read_parquet(processed_file_path)
    return gdf





def compute_heading(lat1, lon1, lat2, lon2):
    """
    Compute compass heading from point 1 to point 2 in degrees.
    0 = North, 90 = East, 180 = South, 270 = West
    """
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    x = math.sin(dLon) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)

    heading = math.degrees(math.atan2(x, y))
    return (heading + 360) % 360





def add_heading_to_route(route):
    gdf = route
    lats = gdf.geometry.y.values
    lons = gdf.geometry.x.values

    headings = []

    for i in range(len(gdf)):
        if i < len(gdf) - 1:
            # heading to next point
            h = compute_heading(lats[i], lons[i], lats[i+1], lons[i+1])
        else:
            # last point: repeat previous heading
            h = headings[-1] if headings else 0
        headings.append(h)

    gdf["heading"] = headings
    return gdf





def add_cumdist_to_route(route):
    gdf = route

    mean_lon = gdf.geometry.x.mean()
    utm_zone = int((mean_lon + 180) / 6) + 1
    utm_crs = f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs"


    gdf_m = gdf.to_crs(utm_crs)

    coords = np.array([[p.x, p.y] for p in gdf_m.geometry])

    segment_distances = np.sqrt(np.sum(np.diff(coords, axis=0)**2, axis=1))
    segment_distances = np.insert(segment_distances, 0, 0)


    cumulative_distance = np.cumsum(segment_distances)

    # Add back to original GeoDataFrame
    gdf["distance_along_m"] = cumulative_distance

    return gdf





def process_gpx_route(route_name):
    route = load_in_gpx(route_name)
    route = add_cumdist_to_route(route)
    route = add_heading_to_route(route)
    processed_file_path = processed_routes_folder_path / f'{route_name}.parquet'
    route.to_parquet(processed_file_path, engine='pyarrow', index=False)  





def get_cord_from_dist_along_route(route, latest_distance):
    gdf = route
    idx = (gdf["distance_along_m"] - latest_distance).abs().idxmin()
    return gdf.iloc[idx]





def get_streetview_image_from_coord(coord_row, fov=90, pitch=0, size="600x400"):
    row = coord_row
    lat = row.geometry.y
    lon = row.geometry.x
    heading = row.get("heading", 0) 

    GOOGLE_API_KEY = 'AIzaSyC8zAxvLoCPbQB5LERW0QNHRc_cLYd1OsI'
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
    img.show()  # opens the image in your default viewer











def freeride_loop(window_title, bbox, capture_interval, total_distance):

    print(f"Logging every {capture_interval}s until distance reaches {total_distance}...")

    start_time = time.time()
    data = []
    latest_distance = 0

    while latest_distance < total_distance:
        ts, latest_distance = read_distance_once(window_title, bbox, start_time, 'km')

        if np.isnan(latest_distance):
            print(f"[{ts:.1f}s] Number: NA")
        else:
            print(f"[{ts:.1f}s] Number: {latest_distance}")

        data.append([ts, latest_distance])
        time.sleep(capture_interval)

    return data





def save_csv(data, output_csv):
    df = pd.DataFrame(data, columns=["timestamp", "distance"])
    df.to_csv(output_csv, index=False)
    print(f"Saved data to: {output_csv}")





















































































































# Graveyard
# # --- Real-time logger ---
# def log_numbers(window_title, bbox, captureinterval, totaldistance, output_csv):
#     """
#     Capture the window region every `interval` seconds for `duration` seconds
#     and save timestamp + number to CSV.
#     """
#     data = []
#     start_time = time.time()


#     print(f"Logging numbers from '{window_title}' every {captureinterval}s for {totaldistance}km...")
#     distance = 0
#     while distance < totaldistance:
#         img = capture_window_region(window_title, bbox)
#         if img:
#             distance = extract_number_from_image(img)
#             timestamp = time.time() - start_time
#             if distance is not None:
#                 print(f"[{timestamp:.1f}s] Number: {distance}")
#                 data.append([timestamp, distance])
#             else:
#                 print(f"[{timestamp:.1f}s] Number: NA")
#                 data.append([timestamp, np.nan])
#         time.sleep(captureinterval)

#     df = pd.DataFrame(data, columns=["timestamp", "distance"])
#     df.to_csv(output_csv, index=False)
#     print(f"[{timestamp:.1f}s] Data saved")