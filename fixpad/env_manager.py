# Third Party Libraries
import pygetwindow as gw
import pyautogui as py

# Standard Library
import subprocess
import time
import ctypes
import base64
import os


def launch_notepadpp(resized_width=960, resized_height=720):
    possible_paths = [
        "C:\\Program Files\\Notepad++\\notepad++.exe",
        "C:\\Program Files (x86)\\Notepad++\\notepad++.exe",
        "C:\\Users\\musta\\Documents\\FixpadTools\\npp.8.6.4.portable.x64\\notepad++.exe",  # <- customize this
    ]

    for path in possible_paths:
        if os.path.exists(path):
            subprocess.Popen([path])
            print(f"✅ Launched Notepad++ from: {path}")
            break
    else:
        raise FileNotFoundError("❌ Could not find Notepad++ in known paths.")

    time.sleep(1.0)

    for window in gw.getWindowsWithTitle("Notepad++"):
        if window.isMaximized:
            window.restore()
        window.resizeTo(resized_width, resized_height)
        window.moveTo(0, 0)
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

    filtered = [
        w for w in windows
        if "File Explorer" not in w.title and "Function List" not in w.title
    ]

    return len(filtered) == 0

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
