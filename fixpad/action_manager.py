# Third Party Libraries
import pyperclip
import pyautogui

# Standard Library
import time
import json

# Custom Project Modules
from util import clean_json_response

# Global delay to adjust the slight pause between actions
delay = 0.2

def bbox_to_center_xy(bbox, screen_width=960, screen_height=720):
    x_min, y_min, x_max, y_max = bbox
    x = (x_min + (x_max - x_min) * 0.25 ) * screen_width # To make it click at the %25 inside the box width
    # x = int((x_min + x_max) / 2 * screen_width)
    y = int((y_min + y_max) / 2 * screen_height)
    return x, y

def execute_actions(actions):
    """
    Executes a list of UI actions using PyAutoGUI.
    
    Args:
        actions (list): A list of actions, each a dict with type and parameters.
    """
    print("Action:")
    for action in actions:
        action_type = action.get("type")

        if action_type == "moveTo":
            x, y = bbox_to_center_xy(action["bbox"])
            if action.get("input_field", True):
                x = x + 60
                print(f"➡️ Moving to ({x}, {y}) with input field adjustment")
            else:
                print(f"➡️ Moving to ({x}, {y})")
            pyautogui.moveTo(x, y, duration=0.3)

        elif action_type == "click":
            print("🖱️ Clicking")
            pyautogui.click()

        elif action_type == "paste":
            print(f"📋 Pasting {action["text"]}")
            text = action["text"]
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
        
        elif action_type == "keyDown":
            key = action["key"]
            print(f"🔽 Holding down key: {key}")
            pyautogui.keyDown(key)
        
        elif action_type == "keyUp":
            key = action["key"]
            print(f"🔼 Releasing key: {key}")
            pyautogui.keyUp(key)

        elif action_type == "dragSelect":
            start_x, start_y = bbox_to_center_xy(action["start_bbox"])
            end_x, end_y = bbox_to_center_xy(action["end_bbox"])
            print(f"🖱️ Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            pyautogui.moveTo(start_x, start_y)
            pyautogui.mouseDown()
            pyautogui.moveTo(end_x, end_y, duration=0.5)  # Smooth drag
            pyautogui.mouseUp()

        else:
            print(f"⚠️ Unknown action type: {action_type}")
        
        time.sleep(delay)  # Slight pause between actions


def parse_actions(response_text):
    """
    Parses the LLM response into structured action commands.
    
    Args:
        response_text (str): Raw response text from the LLM.

    Returns:
        list or None: Parsed action dictionaries or None if parsing fails.
    """
    try:
        # Clean off any ```json wrappers or markdown fences
        # print(f"Raw text: {response_text}") # DEBUG
        clean_text = clean_json_response(response_text)

        # Parse the JSON
        parsed = json.loads(clean_text)

        # Validate expected key
        if "actions" not in parsed:
            raise ValueError("Missing 'actions' field in parsed response.")

        # Validate structure
        actions = parsed["actions"]
        if not isinstance(actions, list):
            raise TypeError("'actions' should be a list.")

        return actions

    except Exception as e:
        print("⚠️ Could not parse model response:", e)
        print("Raw output:\n", response_text)
        return None
