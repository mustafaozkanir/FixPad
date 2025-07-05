# Third Party Libraries
import pygetwindow as gw
import pyautogui as py

# Standard Library
import subprocess
import time
import ctypes
import base64
import os

INSTALLER_DIR = "installers"  # Folder where all installers are stored

INSTALLER_MAP = {
    "npp.6.2.3": "npp.6.2.3.Installer.exe",
    "npp.6.7.4": "npp.6.7.4.Installer.exe",
    "npp.6.8.7": "npp.6.8.7.Installer.exe",
    "npp.6.9":   "npp.6.9.Installer.exe",
    "npp.7.3.3": "npp.7.3.3.Installer.exe",
    "npp.7.5.4": "npp.7.5.4.Installer.exe",
    "npp.7.5.6": "npp.7.5.6.Installer.exe",
    "npp.7.6.2": "npp.7.6.2.Installer.exe",
    "npp.7.6.3": "npp.7.6.3.Installer.exe",
    "npp.7.6.4": "npp.7.6.4.Installer.exe",
    "npp.7.6.6": "npp.7.6.6.Installer.exe",
    "npp.7.7.1": "npp.7.7.1.Installer.exe",
    "npp.7.7":   "npp.7.7.Installer.exe",
    "npp.7.8.1": "npp.7.8.1.Installer.exe",
    "npp.7.8.2": "npp.7.8.2.Installer.exe",
    "npp.7.8.3": "npp.7.8.3.Installer.exe",
    "npp.7.8.5": "npp.7.8.5.Installer.exe",
    "npp.7.8.6": "npp.7.8.6.Installer.exe",
    "npp.7.8"  : "npp.7.8.Installer.exe",
    "npp.7.9.2": "npp.7.9.2.Installer.exe",
    "npp.7.9.5": "npp.7.9.5.Installer.exe",
    "npp.7":     "npp.7.Installer.exe",
    "npp.8.0":   "npp.8.0.Installer.exe",
    "npp.8.1.1": "npp.8.1.1.Installer.exe",
    "npp.8.1.2": "npp.8.1.2.Installer.exe",
    "npp.8.1.3": "npp.8.1.3.Installer.exe",
    "npp.8.1.4": "npp.8.1.4.Installer.exe",
    "npp.8.1.5": "npp.8.1.5.Installer.exe",
    "npp.8.1.9.2":  "npp.8.1.9.2.Installer.exe",
    "npp.8.1.9.3":  "npp.8.1.9.3.Installer.x64.exe",
    "npp.8.1":   "npp.8.1.Installer.exe",
    "npp.8.2.1": "npp.8.2.1.Installer.x64.exe",
    "npp.8.2":   "npp.8.2.Installer.x64.exe",
    "npp.8.3.1": "npp.8.3.1.Installer.x64.exe",
    "npp.8.3.3": "npp.8.3.3.Installer.x64.exe",
    "npp.8.3":   "npp.8.3.Installer.exe",
    "npp.8.4.1": "npp.8.4.1.Installer.x64.exe",
    "npp.8.4.2": "npp.8.4.2.Installer.x64.exe",
    "npp.8.4.3": "npp.8.4.3.Installer.x64.exe",
    "npp.8.4.4": "npp.8.4.4.Installer.x64.exe",
    "npp.8.4.5": "npp.8.4.5.Installer.x64.exe",
    "npp.8.4.6": "npp.8.4.6.Installer.x64.exe",
    "npp.8.4.7": "npp.8.4.7.Installer.x64.exe",
    "npp.8.4.9": "npp.8.4.9.Installer.x64.exe",
    "npp.8.4"  : "npp.8.4.Installer.x64.exe",
    "npp.8.5.4": "npp.8.5.4.Installer.x64.exe",
    "npp.8.5.6": "npp.8.5.6.Installer.x64.exe",
    "npp.8.6.4": "npp.8.6.4.Installer.x64.exe",
    "npp.8.6.5": "npp.8.6.5.Installer.x64.exe",
    "npp.8.6.6": "npp.8.6.6.Installer.x64.exe",
    "npp.8.6.7": "npp.8.6.7.Installer.x64.exe",
    "npp.8.6.8": "npp.8.6.8.Installer.x64.exe",
    "npp.8.6.9": "npp.8.6.9.Installer.x64.exe",
    "npp.8.7.2": "npp.8.7.2.Installer.x64.exe",
    "npp.8.7.4": "npp.8.7.4.Installer.x64.exe",
    "npp.8.7.5": "npp.8.7.5.Installer.x64.exe",
    "npp.8.7.7": "npp.8.7.7.Installer.x64.exe",
    "npp.8.7.8": "npp.8.7.8.Installer.x64.exe",
    "npp.8.7": "npp.8.7.Installer.x64.exe"
}

def install_version(version_key):
    """
    Installs a specific Notepad++ version silently.
    """
    if version_key not in INSTALLER_MAP:
        raise ValueError(f"No installer defined for version: {version_key}")
    
    installer_path = os.path.join(INSTALLER_DIR, INSTALLER_MAP[version_key])

    if not os.path.exists(installer_path):
        raise FileNotFoundError(f"Installer not found at: {installer_path}")

    print(f"🛠️  Installing {version_key} from {installer_path}")

    # Silent install command
    result = subprocess.run([installer_path, "/S"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        print("❌ Installation failed:", result.stderr.decode())
    else:
        print("✅ Installation complete.")


def uninstall_notepadpp():
    """
    Silently uninstalls Notepad++ if present.
    """
    # Standard uninstall path used by Notepad++ installer
    uninstallers = [
        r"C:\Program Files\Notepad++\uninstall.exe",
        r"C:\Program Files (x86)\Notepad++\uninstall.exe"
    ]

    for uninstaller in uninstallers:
        if os.path.exists(uninstaller):
            print(f"🧹 Uninstalling Notepad++ from {uninstaller}")
            subprocess.run([uninstaller, "/S"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(3.0)
            return

    print("⚠️  No uninstall.exe found — Notepad++ can not be uninstalled.")

def switch_to_version(version_key):
    print(f"🔁 Switching to version: {version_key}")
    uninstall_notepadpp()
    time.sleep(2.0)
    install_version(version_key)
    time.sleep(2.0)

def launch_notepadpp(resized_width=960, resized_height=720):
    possible_paths = [
        "C:\\Program Files\\Notepad++\\notepad++.exe",
        "C:\\Program Files (x86)\\Notepad++\\notepad++.exe",
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

