# Third Party Libraries
from pywinauto import Application
from pywinauto.findwindows import find_elements
import pyperclip
import pyautogui

# Standard Library
import time
import json
import os

# Custom Project Modules
from env_manager import launch_notepadpp
from util import clean_json_response

# Global delay to adjust the slight pause between actions
delay = 0.2

def bbox_to_center_xy(bbox, screen_width=960, screen_height=720):
    x_min, y_min, x_max, y_max = bbox
    x = (x_min + (x_max - x_min) * 0.25 ) * screen_width # To make it click at the %25 inside the box width
    # x = int((x_min + x_max) / 2 * screen_width)
    y = int((y_min + y_max) / 2 * screen_height)
    return x, y

def get_main_notepadpp_window():
    try:
        # Find all windows with Notepad++ in the title
        windows = find_elements(title_re=".*Notepad.*", backend="uia")

        # Filter: must contain ' - Notepad++' and NOT 'File Explorer'
        main_candidates = [
            w for w in windows
            if " - Notepad++" in w.name and "File Explorer" not in w.name
        ]

        if not main_candidates:
            raise RuntimeError("❌ Main Notepad++ window not found.")

        main_window = main_candidates[0]
        app = Application(backend="uia").connect(handle=main_window.handle)
        return app.window(handle=main_window.handle)

    except Exception as e:
        print(f"❌ Failed to get main Notepad++ window: {e}")
        return None

def find_best_matching_control(window, label):
    """
    Matching priority (in order):
    1. Exact match (case-insensitive)
    2. Suffix match (e.g., label="Define" matches "Define your language...")
    3. Substring match (fallback, may be noisy)
    """
    try:
        all_controls = window.descendants()
        label_lower = label.strip().lower()

        # 1. Exact match
        exact_matches = [ctrl for ctrl in all_controls 
                         if ctrl.window_text().strip().lower() == label_lower]
        if exact_matches:
            return prioritize_control_types(exact_matches)

        # 2. Suffix match (e.g. label="Define" matches "Define your language...")
        suffix_matches = [ctrl for ctrl in all_controls 
                          if ctrl.window_text().strip().lower().endswith(label_lower)]
        if suffix_matches:
            return prioritize_control_types(suffix_matches)

        # 3. Substring match (fallback)
        substring_matches = [ctrl for ctrl in all_controls 
                             if label_lower in ctrl.window_text().strip().lower()]
        if substring_matches:
            return prioritize_control_types(substring_matches)

        print(f"❌ No matches found for '{label}'.")
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
    combobox_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() == "ComboBox"]
    other_controls = [ctrl for ctrl in matches if ctrl.friendly_class_name() not in ["Edit", "RadioButton", "Button", "MenuItem", "GroupBox", "ComboBox"]]

    for group in [edit_controls, radio_controls, button_controls, menuitem_controls, groupbox_controls, combobox_controls, other_controls]:
        if group:
            print(group) 
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
            print(f"➡️  Moving to ({x}, {y})")
            pyautogui.moveTo(x, y, duration=0.3)

        elif action_type == "click":
            # Connect to Notepad++
            window = get_main_notepadpp_window()

            label = action.get("label", None)

            print(f"🖱️  Trying to click '{label}' via Pywinauto first...")

            control = find_best_matching_control(window, label)
            if control and control.element_info.enabled:
                rect = control.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2
                pyautogui.moveTo(center_x, center_y, duration=0.3)
                if control.friendly_class_name() == "Edit":
                    pyautogui.doubleClick()
                    print(f"✅  Double-clicked on '{label}' ({control.friendly_class_name()}) successfully.")
                elif control.friendly_class_name() == "Static":
                    rect = control.rectangle()
                    x = rect.right + 20  # Move 20px to the right of label
                    y = (rect.top + rect.bottom) // 2
                    pyautogui.moveTo(x, y, duration=0.3)
                    pyautogui.click()
                    print(f"🡆 Clicked next to Static label '{label}' (assumed input field)")
                else:
                    pyautogui.click()
                    print(f"✅  Clicked on '{label}' ({control.friendly_class_name()}) successfully.")

            else:
                print(f"⏩  No matching control found. Clicking at current mouse position.")
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
            pyautogui.moveTo(start_x, start_y, duration=0.5)
            pyautogui.keyDown('alt')
            pyautogui.mouseDown()
            pyautogui.moveTo(end_x, end_y, duration=0.8)
            time.sleep(0.2)
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
    
def replay_trajectory(bug_id, log_dir="run_logs"):
    launch_notepadpp()
    path_to_trajectory_json = os.path.join(log_dir, bug_id, "trajectory.json")
    time_log_path = os.path.join(log_dir, bug_id, "time.txt")

    if not os.path.exists(path_to_trajectory_json):
        print(f"❌ No trajectory found for bug ID '{bug_id}' at {path_to_trajectory_json}")
        return

    with open(path_to_trajectory_json, "r") as f:
        trajectory = json.load(f)

    print(f"\n▶️  Replaying trajectory for {bug_id}...")
    start_time = time.time()

    for step in trajectory:
        actions = step["actions"]
        print(f"\n🔁  Replaying step: {step['thought']}")
        execute_actions(actions)
        time.sleep(1.0)

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n⏱ Total verification (replay) time: {elapsed:.2f} seconds")

    # Append verification time to time.txt
    with open(time_log_path, "a") as f:
        f.write(f"Verification Time: {elapsed:.4f}\n")

    print(f"✅ Appended verification time to {time_log_path}")

