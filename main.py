import pygetwindow as gw
import mss
from PIL import Image

# List all window titles
titles = gw.getAllTitles()
print("All window titles:", titles)

# Find the QuickTime window
qt_title = None
for t in titles:
    if "Movie Recording" in t:  # Adjust if your window title is slightly different
        qt_title = t
        break

if not qt_title:
    raise Exception("QuickTime Movie Recording window not found!")

window = gw.getWindowsWithTitle(qt_title)[0]

# Get window coordinates
left, top, width, height = window.left, window.top, window.width, window.height

# Capture the window
with mss.mss() as sct:
    monitor = {"top": top, "left": left, "width": width, "height": height}
    screenshot = sct.grab(monitor)
    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
    img.save("iphone_screenshot.png")

print("Screenshot saved as iphone_screenshot.png")
