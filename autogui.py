import pyautogui

pyautogui.FAILSAFE = False

pyautogui.moveTo(1800, 0)      # Move mouse to position (x=100, y=200)
pyautogui.click()               # Left click
pyautogui.sleep(4)
pyautogui.moveTo(1880, 20) 
#pyautogui.rightClick()          # Right click
pyautogui.doubleClick()         # Double click
pyautogui.sleep(4)
pyautogui.doubleClick()
#pyautogui.moveRel(0, 50)        # Move relative to current position