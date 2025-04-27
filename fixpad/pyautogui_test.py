import pygetwindow as gw
import pyautogui as py
import time

def bbox_to_center_xy(bbox, screen_width=960, screen_height=720):
    x_min, y_min, x_max, y_max = bbox
    x = int((x_min + x_max) / 2 * screen_width)
    # x = (x_min + (x_max - x_min) * 0.25 ) * screen_width # To make it click to more left
    y = int((y_min + y_max) / 2 * screen_height)
    return x, y


def execute_drag_select(start_bbox, end_bbox):
    start_x, start_y = bbox_to_center_xy(start_bbox)
    end_x, end_y = bbox_to_center_xy(end_bbox)

    
    time.sleep(0.2)
    py.moveTo(start_x, start_y)
    py.keyDown("alt")
    py.mouseDown()
    py.moveTo(end_x, end_y, duration=0.2)  # Smooth drag
    py.mouseUp()
    time.sleep(0.2)
    py.keyUp("alt")

"""
Detects if the application window no longer exists (fully closed)
"""
def detect_window_closed(window_title="Notepad++"):
    windows = gw.getWindowsWithTitle(window_title)
    return len(windows) == 0

time.sleep(3)
py.click((202+319)/2, (485+501)/2)

# print(detect_window_closed())




