import subprocess
import os

def uninstall_notepadpp():
    uninstall_path = r"C:\Program Files (x86)\Notepad++\uninstall.exe"
    alternative_uninstall_path = r"C:\Program Files\Notepad++\uninstall.exe"
    if os.path.exists(uninstall_path):
        print("🗑️ Uninstalling Notepad++ silently...")
        try:
            subprocess.run([uninstall_path, "/S"], check=True)
            print("✅ Notepad++ uninstalled.")
        except subprocess.CalledProcessError as e:
            print("❌ Uninstallation failed:", e)

    elif os.path.exists(alternative_uninstall_path):
        print("🗑️ Uninstalling Notepad++ silently...")
        try:
            subprocess.run([alternative_uninstall_path, "/S"], check=True)
            print("✅ Notepad++ uninstalled.")
        except subprocess.CalledProcessError as e:
            print("❌ Uninstallation failed:", e)
    else:
        print("⚠️ Notepad++ is not installed at the default path.")

uninstall_notepadpp()