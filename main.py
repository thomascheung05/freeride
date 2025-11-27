import ctypes
from ctypes import wintypes
import win32gui
import win32ui




def capture_window(filename="window_capture.png"):
    hwnd = '329678'
    # hwnd = win32gui.FindWindow(None, title)
    if not hwnd:
        print("Window not found!")
        return

    # Get window size
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top

    # Get device context
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(bmp)

    # Call PrintWindow via ctypes
    PW_RENDERFULLCONTENT = 0x00000002
    ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), PW_RENDERFULLCONTENT)

    bmp.SaveBitmapFile(saveDC, filename)

    # Free resources
    win32gui.DeleteObject(bmp.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    print(f"Captured {filename}")

capture_window()





# def list_letsview_windows():
#     def enum_windows(hwnd, results):
#         title = win32gui.GetWindowText(hwnd)
#         if "LetsView" in title:
#             results.append((hwnd, title))
#     windows = []
#     win32gui.EnumWindows(enum_windows, windows)
#     return windows
# for hwnd, title in list_letsview_windows():
#     print(f"HWND: {hwnd}, Title: {title}")





# WINDOW_TITLE  = "LetsView"

# def get_window(title):
#     windows = gw.getWindowsWithTitle(title)
#     if not windows:
#         return None
#     return windows[0]

# def main():
#     print("Looking for LetsView window...")
#     while True:
#         window = get_window(WINDOW_TITLE)
#         if window is None:
#             print("Window not found. Waiting...")
#             time.sleep(2)
#             continue

#         # Capture the entire window
#         left, top, width, height = window.left, window.top, window.width, window.height
#         screenshot = pyautogui.screenshot(region=(left, top, width, height))
        
#         # Save the screenshot
#         screenshot.save("letsview_capture.png")
#         print(f"Screenshot saved! Size: {width}x{height}")
#         break  # stop after one capture

# if __name__ == "__main__":
#     main()
    