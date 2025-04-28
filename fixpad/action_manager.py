# Third Party Libraries
from pywinauto import Application
import pyperclip
import pyautogui

# Standard Library
import time
import json
import re

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

def find_best_matching_control(window, label):
    """
    Finds the best matching control based on:
    1. Exact match priority
    2. Shortest window text
    3. Friendly control types (Edit > RadioButton > Button > Other)
    """
    try:
        all_controls = window.descendants()

        # First, exact matches
        exact_matches = [ctrl for ctrl in all_controls 
                         if ctrl.window_text().strip().lower() == label.strip().lower()]
        
        if exact_matches:
            print(f"✅ Exact match found for '{label}'.")
            return prioritize_control_types(exact_matches)

        # No exact match, fallback to partial matches
        regex_matches = [ctrl for ctrl in all_controls 
                         if ctrl.window_text() and re.search(label, ctrl.window_text(), re.IGNORECASE)]
        
        if regex_matches:
            print(f"🔎 {len(regex_matches)} partial matches found for '{label}'.")
            # Sort by shortest window_text length
            regex_matches.sort(key=lambda ctrl: len(ctrl.window_text()))
            return prioritize_control_types(regex_matches)

        print(f"❌ No matching controls found for '{label}'.")
        return None

    except Exception as e:
        print(f"⚠️ Error during control search: {e}")
        return None

def prioritize_control_types(matches):
    """
    Prefer Edit > RadioButton > Button > Anything else.
    """
    edit_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() == "Edit"]
    radio_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() == "RadioButton"]
    button_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() == "Button"]
    menuitem_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() == "MenuItem"]
    groupbox_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() == "GroupBox"]
    other_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() not in ["Edit", "RadioButton", "Button", "MenuItem", "GroupBox"]]

    for group in [edit_controls, radio_controls, button_controls, menuitem_controls, groupbox_controls, other_controls]:
        if group:
            return group[0]

    return None

def line_to_position(line_number):
    """Map a line number to (x, y) screen coordinate for your editor."""
    x = 100
    y_start = 111
    line_height = 17
    y = y_start + (line_number - 1) * line_height
    return (x, y)


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
            """
            if action.get("input_field", True):
                x = x + 60
                print(f"➡️ Moving to ({x}, {y}) with input field adjustment")
            else:
            """
            print(f"➡️ Moving to ({x}, {y})")
            pyautogui.moveTo(x, y, duration=0.3)

        elif action_type == "click":
            # Connect to Notepad++
            try:
                app = Application(backend="uia").connect(title_re=".*Notepad.*")
                window = app.window(title_re=".*Notepad.*")
            except Exception as e:
                print(f"❌  Could not connect to Notepad++ window: {e}")
                window = None

            label = action.get("label", None)

            print(f"🖱️  Trying to click '{label}' via Pywinauto first...")

            control = find_best_matching_control(window, label)
            if control:
                rect = control.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2
                pyautogui.moveTo(center_x, center_y, duration=0.3)
                pyautogui.doubleClick()
                print(f"✅  Double-clicked on '{label}' ({control.friendly_class_name()}) successfully.")

            else:
                print(f"⏩ No matching control found. Clicking at current mouse position.")
                pyautogui.click()

        elif action_type == "paste":
            print(f"📋  Pasting {action["text"]}")
            text = action["text"]
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")

        elif action_type == "hotkey":
            keys = action.get("keys", [])
            print(f"🎹  Pressing hotkey: {keys}")
            pyautogui.hotkey(*keys)
        
        elif action_type == "highlight":
            start_line = action.get("start_line")
            end_line = action.get("end_line")
            print(f"🖱️  Highlighting lines {start_line} to {end_line}")

            start_x, start_y = line_to_position(start_line)
            end_x, end_y = line_to_position(end_line)

            # Click at start
            pyautogui.moveTo(end_x, end_y, duration=0.5)
            pyautogui.click()
            time.sleep(0.3)

            # Shift+Click at end
            pyautogui.keyDown('shift')
            pyautogui.moveTo(start_x, start_y, duration=0.5)
            pyautogui.click()
            pyautogui.keyUp('shift')

        elif action_type == "multi_select":
            start_line = action.get("start_line")
            end_line = action.get("end_line")
            print(f"🖱️  Multi-selecting (Column mode) lines {start_line} to {end_line}")

            start_x, start_y = line_to_position(start_line)
            end_x, end_y = line_to_position(end_line)

            # Hold Alt key for column mode
            pyautogui.keyDown('alt')
            pyautogui.moveTo(start_x, start_y, duration=0.5)
            pyautogui.mouseDown()
            pyautogui.moveTo(end_x, end_y, duration=0.5)
            pyautogui.mouseUp()
            pyautogui.keyUp('alt')


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
