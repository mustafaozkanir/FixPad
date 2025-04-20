# Third Party Libraries
import pygetwindow as gw
import pyautogui as py

# Standard Library
import subprocess
import time

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