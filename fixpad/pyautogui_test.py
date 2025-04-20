import pyautogui as py

def bbox_to_center_xy(bbox, screen_width=960, screen_height=720):
    x_min, y_min, x_max, y_max = bbox
    x = int((x_min + x_max) / 2 * screen_width)
    y = int((y_min + y_max) / 2 * screen_height)
    return x, y

py.sleep(2)
py.moveTo(108, 140)
py.click()