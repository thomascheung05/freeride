
import pytesseract
import time
import time
import pandas as pd
import numpy as np

from screencapture import capture_window_region









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
def log_numbers(window_title, bbox, captureinterval, totaldistance, output_csv):
    """
    Capture the window region every `interval` seconds for `duration` seconds
    and save timestamp + number to CSV.
    """
    data = []
    start_time = time.time()


    print(f"Logging numbers from '{window_title}' every {captureinterval}s for {totaldistance}km...")
    number = 0
    while True:
        img = capture_window_region(window_title, bbox)
        if img:
            number = extract_number_from_image(img)
            timestamp = time.time() - start_time
            if number is not None:
                print(f"[{timestamp:.1f}s] Number: {number}")
                data.append([timestamp, number])
            else:
                print(f"[{timestamp:.1f}s] Number: NA")
                data.append([timestamp, np.nan])
        last_save_time = 0
        if time.time() - last_save_time >= captureinterval*2:
            df = pd.DataFrame(data, columns=["timestamp", "number"])
            df.to_csv(output_csv, index=False)
            last_save_time = time.time()
            print(f"[{timestamp:.1f}s] Data saved")
        time.sleep(captureinterval)