import subprocess
import os
import ctypes
import pyautogui


# Check if script is running with admin rights
if not ctypes.windll.shell32.IsUserAnAdmin():
    print("❌ Please run this script as Administrator!")
    exit(1)

# Define full path to the installer
installer_path = r"C:\Users\musta\Desktop\notepad_installers\npp.7.9.2.Installer.exe"

# Confirm the file exists
if not os.path.exists(installer_path):
    print(f"❌ Installer not found at: {installer_path}")
else:
    print(f"🛠️ Installing Notepad++ v7.9.2 from: {installer_path}")

    try:
        # Run silent installation
        subprocess.run([installer_path, "/S"], check=True)
        print("✅ Notepad++ v7.9.2 installed silently.")
    except subprocess.CalledProcessError as e:
        print("❌ Installation failed:", e)


# Path to notepad++.exe (change this to wherever you installed or extracted it)
npp_path = r"C:\Program Files (x86)\Notepad++\notepad++.exe"

# Launch it!
subprocess.Popen(npp_path)

pyautogui.sleep(5)
pyautogui.click(60, 60)