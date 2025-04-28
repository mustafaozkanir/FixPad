import pygetwindow as gw
import pyautogui as py, pyautogui
import time

def bbox_to_center_xy(bbox, screen_width=960, screen_height=720):
    x_min, y_min, x_max, y_max = bbox
    x = int((x_min + x_max) / 2 * screen_width)
    # x = (x_min + (x_max - x_min) * 0.25 ) * screen_width # To make it click to more left
    y = int((y_min + y_max) / 2 * screen_height)
    return x, y

def line_to_position(line_number):
    """Map a line number to (x, y) screen coordinate for your editor."""
    x = 100
    y_start = 111
    line_height = 17
    y = y_start + (line_number - 1) * line_height
    return (x, y)

def execute_highlight(start_bbox, end_bbox):
        start_line = action.get("start_line")
        end_line = action.get("end_line")
        print(f"🖱️ Highlighting lines {start_line} to {end_line}")

        start_x, start_y = line_to_position(start_line)
        end_x, end_y = line_to_position(end_line)

        # Click at start
        pyautogui.moveTo(start_x, start_y, duration=0.3)
        pyautogui.click()
        time.sleep(0.3)

        # Shift+Click at end
        pyautogui.keyDown('shift')
        pyautogui.moveTo(end_x, end_y, duration=0.3)
        pyautogui.click()
        pyautogui.keyUp('shift')
        

"""
Detects if the application window no longer exists (fully closed)
"""
def detect_window_closed(window_title="Notepad++"):
    windows = gw.getWindowsWithTitle(window_title)
    return len(windows) == 0

time.sleep(2)
# pyautogui.click(100,111)


start_line = 1
end_line = 28
print(f"🖱️ Multi-selecting (Column mode) lines {start_line} to {end_line}")

start_x, start_y = line_to_position(start_line)
end_x, end_y = line_to_position(end_line)

# Hold Alt key for column mode
pyautogui.keyDown('alt')
pyautogui.moveTo(start_x, start_y, duration=0.5)
print(pyautogui.position())
pyautogui.mouseDown()
pyautogui.moveTo(end_x, end_y, duration=0.5)
pyautogui.mouseUp()
pyautogui.keyUp('alt')




