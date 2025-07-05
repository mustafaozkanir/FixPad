import time
from env_manager import detect_crash  # import your detection logic

print("🔍 Watching for Notepad++ crash...")

while True:
    if detect_crash():
        print("❗Crash detected!")
        break
    else:
        print("✅ No crash.")
    time.sleep(2)  # Check every 2 seconds