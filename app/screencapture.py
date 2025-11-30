import win32gui, win32ui, ctypes
from PIL import Image
import time
from PIL import Image
import win32gui
import pyautogui
import time
import os
import pytesseract
import numpy as np


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





def get_window_relative_bbox(window_title,save_screenshot_path):
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
    screenshot = capture_window_region(window_title, bbox)
    if screenshot:
        screenshot.save(save_screenshot_path)
        print(f"Screenshot of bbox saved to {os.path.abspath(save_screenshot_path)}")
    else:
        print("Failed to capture screenshot of bbox.")
    return bbox





def capture_window_region(title, bbox):
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
    
    # free up resources 
    win32gui.DeleteObject(bmp.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return cropped_img





def extract_number_from_image(img):
    tesseract_path = r"C:\Users\Thomas\Main\freeride\tesseract\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    text = pytesseract.image_to_string(img, config='--psm 7')  # single line
    text = text.strip().replace(',', '')
    try:
        return float(text)
    except ValueError:
        return None
    




def read_distance_once(window_title, bbox, start_time, distance_units):
    """
    Captures window, extracts number, returns (timestamp, distance or NaN)
    """
    img = capture_window_region(window_title, bbox)
    timestamp = time.time() - start_time

    if img is None:
        return timestamp, np.nan

    distance = extract_number_from_image(img)
    if distance is None:
        return timestamp, np.nan
    else:
        if distance_units == 'km':
            distance = distance * 1000
        if distance_units == 'miles':
            distance = distance * 1609

    return timestamp, distance
