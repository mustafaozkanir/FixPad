from pywinauto import Application
from pywinauto.findwindows import find_elements
from env_manager import detect_crash
import pyautogui as py
from time import sleep


sleep(3)
py.hotkey('altleft', 'shiftleft', 'right')