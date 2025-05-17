from pywinauto import Application
from pywinauto.findwindows import find_elements
from env_manager import detect_crash
import pyautogui as py
from time import sleep

if(detect_crash()):
    print("✅  Bug is successfully reproduced!")

sleep(2)
py.click(372.5757694244385, 337)
