import ctypes
from ctypes import wintypes
import win32gui
import win32ui




def capture_window(title, filename="window_capture.png"):
    hwnd = win32gui.FindWindow(None, title)
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

capture_window('LetsView [Cast]')





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


