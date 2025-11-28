

from app.data import log_numbers

# --- Usage ---
window_title = "LetsView [Cast]"
bbox = (9, 379, 183, 449)  # window-relative coordinates


#get_window_relative_bbox("LetsView [Cast]")
# Log numbers every 1 second for 2 minutes (120s)
captureinterval = 5
totaldistance =2
log_numbers(window_title, bbox, captureinterval, totaldistance, output_csv="speed_data.csv")



