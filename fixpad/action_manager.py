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
                print(f"❌ Could not connect to Notepad++ window: {e}")
                window = None

            label = action.get("label", None)

            print(f"🖱️ Trying to click '{label}' via Pywinauto first...")

            found = False

            if label and window:
                try:
                    # 1. Get all descendants
                    all_controls = window.descendants()

                    # 2. Filter manually based on regex matching
                    matches = [ctrl for ctrl in all_controls if ctrl.window_text() and re.search(label, ctrl.window_text(), re.IGNORECASE)]
                    print(f"🔎 Found {len(matches)} matching controls for label '{label}'")

                    if matches:
                        # Step 2: Prioritize controls
                        edit_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() == "Edit"]
                        radio_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() == "RadioButton"]
                        button_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() == "Button"]
                        other_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() not in ["Edit", "RadioButton", "Button"]]

                        # Try in order
                        chosen_control = None
                        if edit_controls:
                            chosen_control = edit_controls[0]
                            print("✅ Prioritized Edit control.")
                        elif radio_controls:
                            chosen_control = radio_controls[0]
                            print("✅ Prioritized RadioButton control.")
                        elif button_controls:
                            chosen_control = button_controls[0]
                            print("✅ Prioritized Button control.")
                        elif other_controls:
                            chosen_control = other_controls[0]
                            print("✅ Using other control.")

                        if chosen_control:
                            rect = chosen_control.rectangle()
                            center_x = (rect.left + rect.right) // 2
                            center_y = (rect.top + rect.bottom) // 2
                            pyautogui.moveTo(center_x, center_y, duration=0.3)
                            pyautogui.doubleClick()
                            print(f"✅ Double-clicked on '{label}' ({chosen_control.friendly_class_name()}) successfully.")
                            found = True

                except Exception as e:
                    print(f"⚠️ Error during control search: {e}")

            if not found:
                print(f"⏩ No matching control found. Falling back to clicking at current mouse position.")
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
