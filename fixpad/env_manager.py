# Third Party Libraries
import pygetwindow as gw
import pyautogui as py

# Standard Library
import subprocess
import time
import ctypes
import base64


def launch_notepadpp(resized_width=960, resized_height=720):
    # Launch Notepad++
    subprocess.Popen(["C:\\Program Files\\Notepad++\\notepad++.exe"])
    time.sleep(1.0)  # Wait for window to appear

    for window in gw.getWindowsWithTitle("Notepad++"):
        if window.isMaximized:
            window.restore()
        window.resizeTo(resized_width, resized_height)
        window.moveTo(0, 0)  # Move it to top-left corner
        break

def capture_notepadpp_only(save_path):
    for window in gw.getWindowsWithTitle("Notepad++"):
        if window.visible:
            x, y, width, height = window.left, window.top, window.width, window.height
            screenshot = py.screenshot(region=(x, y, width, height))
            screenshot.save(save_path)
            return

def take_screenshot(save_path):
    screenshot = py.screenshot()
    screenshot.save(save_path)
    return save_path

def save_annotated_image(image_content, save_path):
    # Decode the image
    image_data = base64.b64decode(image_content)

    # Write to a PNG file
    with open(save_path, "wb") as f:
        f.write(image_data)

    print("Saved: ", save_path)

"""
Detects if a window is hung
"""
def detect_window_hung(window_title="Notepad++"):
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        return False  # No window found → consider crashed

    hwnd = windows[0]._hWnd # Get the raw Windows handle (internal)

    result = ctypes.windll.user32.IsHungAppWindow(hwnd)

    return result == 1  # Returns True if window is hung (unresponsive)

"""
Detects crash with popups.
Looks for any window whose title includes:
Exception, Win32Excpetion, or stopped working
"""
def detect_crash_popup():
    windows = gw.getAllTitles()
    for title in windows:
        if "Exception" in title or "stopped working" in title or "Win32Exception" in title:
            return True
    return False

"""
Detects if the application window no longer exists (fully closed)
"""
def detect_window_closed(window_title="Notepad++"):
    windows = gw.getWindowsWithTitle(window_title)
    return len(windows) == 0

"""
Full crash detection combining all methods:
- Window Hung
- Crash Popup
- Window Closed
"""
def detect_crash():
    time.sleep(5.0) 
    is_crashed = detect_crash_popup()
    is_hung = detect_window_hung()
    is_closed = detect_window_closed()
    
    return is_hung or is_crashed or is_closed
