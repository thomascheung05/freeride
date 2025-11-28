import win32gui, win32ui, ctypes
from PIL import Image
import pytesseract
import time
from PIL import Image
import win32gui
import pyautogui
import time
import pandas as pd
import os


def list_letsview_windows():
    def enum_windows(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "LetsView" in title:
            results.append((hwnd, title))
    
    windows = []
    win32gui.EnumWindows(enum_windows, windows)
    
    if not windows:
        print("No LetsView windows found.")
    else:
        for hwnd, title in windows:
            print(f"HWND: {hwnd}, Title: {title}")



def get_window_relative_bbox(window_title):
    # Find the window
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print("Window not found!")
        return None

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
    return bbox




def capture_window_region(title, bbox, filename="window_capture.png"):
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

    cropped_img = img.crop(bbox)    # crops the image to only the bounding box
    cropped_img.save(filename)      # Saves image
    
    # free up resources 
    win32gui.DeleteObject(bmp.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return cropped_img





# bbox = get_window_relative_bbox("LetsView [Cast]")
bbox = (129, 266, 264, 342)  # left, top, right, bottom relative to window
window_title = "LetsView [Cast]"
data = []
start_time = time.time()



# --- OCR function ---
def extract_number_from_image(img):
    text = pytesseract.image_to_string(img, config='--psm 7')  # single line
    text = text.strip().replace(',', '')
    try:
        return float(text)
    except ValueError:
        return None

tesseract_path = r"C:\Users\Thomas\Main\freeride\tesseract\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# --- Real-time logger ---
def log_numbers(window_title, bbox, interval=1.0, duration=60, output_csv="numbers.csv"):
    """
    Capture the window region every `interval` seconds for `duration` seconds
    and save timestamp + number to CSV.
    """
    data = []
    start_time = time.time()
    end_time = start_time + duration

    print(f"Logging numbers from '{window_title}' every {interval}s for {duration}s...")

    while time.time() < end_time:
        img = capture_window_region(window_title, bbox)
        if img:
            number = extract_number_from_image(img)
            timestamp = time.time() - start_time
            if number is not None:
                print(f"[{timestamp:.1f}s] Number: {number}")
                data.append([timestamp, number])
            else:
                print(f"[{timestamp:.1f}s] Could not read number.")
        time.sleep(interval)

    # Save CSV
    df = pd.DataFrame(data, columns=["timestamp", "number"])
    df.to_csv(output_csv, index=False)
    print(f"Data saved to {os.path.abspath(output_csv)}")

# --- Usage ---
window_title = "LetsView [Cast]"
bbox = (129, 266, 264, 342)  # window-relative coordinates

# Log numbers every 1 second for 2 minutes (120s)
log_numbers(window_title, bbox, interval=1, duration=120, output_csv="speed_data.csv")



