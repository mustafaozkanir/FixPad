import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part, Content

import pyautogui as py
import json
import os
from datetime import datetime

from prompts import system_prompt, observation_prompt, reflexion_prompt, AVAILABLE_ACTIONS, EXAMPLE_RESPONSE
from omniparser import get_parsed_image_content
from action_manager import parse_actions, execute_actions
from util import clean_json_response

import subprocess
import time
import pygetwindow as gw
import base64

def launch_notepadpp(resized_width=1280, resized_height=720):
    # Launch Notepad++
    subprocess.Popen(["C:\\Program Files\\Notepad++\\notepad++.exe"])
    time.sleep(1.5)  # Wait for window to appear

    for window in gw.getWindowsWithTitle("Notepad++"):
        if window.isMaximized:
            window.restore()
        window.resizeTo(resized_width, resized_height)
        window.moveTo(0, 0)  # Move it to top-left corner
        break

def capture_notepadpp_only(save_path):
    for window in gw.getWindowsWithTitle("Notepad++"):
        if window.visible:
            x, y, width, height = window.left, window.top, window.width, window.height
            screenshot = py.screenshot(region=(0, 0, 1280, 720))
            screenshot.save(save_path)
            return

def take_screenshot(save_path):
    screenshot = py.screenshot()
    screenshot.save(save_path)
    return save_path

class FixAgent:
    def __init__(self, project_id="gen-lang-client-0225271187", location="us-central1", system=None):
        
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name = "gemini-2.0-flash",
                                     generation_config={
                                        "temperature": 0,
                                        "response_mime_type": "application/json"
                                        }
                                     )

        self.messages = []
        self.trajectory = []
        if system is not None:
            self.messages.append(f"SYSTEM: {system}")

    def __call__(self, message="", screenshot_path=None):
        if message:
            self.messages.append(f"USER: {message}")
        
        result = self.execute(screenshot_path)
        self.maintain_trajectory(result)
        self.messages.append(f"ASSISTANT: {result}")
        return result

    def execute(self, screenshot_path):
        if screenshot_path:
            with open(screenshot_path, "rb") as f:
                image_bytes = f.read()
            
            # Create the image part
            image_part = Part.from_data(data=image_bytes, mime_type="image/png")
            
            # Combine all string messages into one if there are multiple
            if isinstance(self.messages, list):
                text_prompt = "\n".join(self.messages)
            else:
                text_prompt = self.messages
            
            # Now pass the image and the combined text
            response = self.model.generate_content([
                image_part,
                text_prompt
            ])
        else:
            response = self.model.generate_content(self.messages)

        return response.text
    
    def maintain_trajectory(self, result):
        try:
            parsed = json.loads(clean_json_response(result))
            thought = parsed.get("thought", "")
            actions = parsed.get("actions", [])
            if thought and isinstance(actions, list):
                self.trajectory.append({"thought": thought, "actions": actions})
        except Exception as e:
            print("Failed to parse thought/action for trajectory:", e)

class ReflectionAgent():
    def __init__(self, project_id="gen-lang-client-0225271187", location="us-central1"):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0,
                "response_mime_type": "application/json"
            }
        )
        self.messages = []
    
    def __call__(self, message="", screenshot_path=None):
        if message:
            self.messages.append(f"USER: {message}")

        result = self.execute(screenshot_path)
        self.messages.append(f"ASSISTANT: {result}")
        return result
    
    def execute(self, screenshot_path):
        if screenshot_path:
            with open(screenshot_path, "rb") as f:
                image_bytes = f.read()
            
            # Create the image part
            image_part = Part.from_data(data=image_bytes, mime_type="image/png")
            
            # Combine all string messages into one if there are multiple
            if isinstance(self.messages, list):
                text_prompt = "\n".join(self.messages)
            else:
                text_prompt = self.messages
            
            # Now pass the image and the combined text
            response = self.model.generate_content([
                image_part,
                text_prompt
            ])
        else:
            response = self.model.generate_content(self.messages)

        return response.text
    

def agent_loop(bug_report, max_iterations):
    os.makedirs("screenshots", exist_ok=True)

    launch_notepadpp()

    # STEP 1: Take initial screenshot
    initial_screenshot_path = f"screenshots/step_0_init.png"
    capture_notepadpp_only(initial_screenshot_path)

    # STEP 2: Parse the image
    parsed_content, image_content = get_parsed_image_content(initial_screenshot_path)

    # STEP 3: Format the system prompt with bug report and parsed content
    formatted_prompt = system_prompt.format(
        available_actions = AVAILABLE_ACTIONS,
        bug_report=bug_report,
        parsed_content=json.dumps(parsed_content, indent=2),
        example_response = EXAMPLE_RESPONSE
    )

    # print(formatted_prompt)

    # STEP 4: Create agent with full system prompt
    fix_agent = FixAgent(system=formatted_prompt)

    # STEP 6: Create reflection agent as well.
    reflection_agent = ReflectionAgent()  

    # STEP 6: Run loop with screenshot + observation each time
    for i in range(1, max_iterations + 1):
        print(f"\n--- Iteration {i} ---")

        # Step i.1: Ask the model what to do
        result = fix_agent()
        print(result)

        # Step i.2: Parse and execute actions
        actions = parse_actions(result)
        print(actions)
        execute_actions(actions)

        # Step i.3: Take new screenshot
        screenshot_path = f"screenshots/step_{i}.png"
        capture_notepadpp_only(screenshot_path)

        # Step i.4: Parse screenshot
        parsed_content, image_content = get_parsed_image_content(screenshot_path)

        # Step i.5: Reflexion evaluation
        formatted_reflexion_prompt = reflexion_prompt.format(
            available_actions = AVAILABLE_ACTIONS,
            bug_report=bug_report,
            trajectory=json.dumps(fix_agent.trajectory, indent=2),
            parsed_content=json.dumps(parsed_content, indent=2)
        )

        reflection_output = reflection_agent(formatted_reflexion_prompt, screenshot_path)
        print("Reflection Output:\n", reflection_output)

        # Step i.5: Update with new observation
        formatted_observation_prompt = observation_prompt.format(
            bug_report = bug_report,
            trajectory=json.dumps(fix_agent.trajectory, indent=2),
            reflection=reflection_output,
            parsed_screenshot=json.dumps(parsed_content, indent=2),
            available_actions = AVAILABLE_ACTIONS,
            example_response = EXAMPLE_RESPONSE
        )        
        fix_agent(formatted_observation_prompt, screenshot_path)


# bug_report = "STR: Make sure no text is selected. Edit -> Paste Special -> Binary Content Copy. Result: NPP crashes."

bug_report = """Paste the following lines in a new document:

Test
Test
Test
Test
Test

Place the caret at line 3.
Go to View → Hide Lines.
Place the caret at line 2.
Go to View → Hide Lines.
Click on the show-lines markers.

You should get this:
(Visual showing lines 2-4 collapsed.)

Click on the single show-lines marker.

Result:
Notepad++ crashes."""


agent_loop(bug_report=bug_report, max_iterations=19)




"""
fix_agent = FixAgent(system=prompt)
next_prompt = ""
i = 0
while i < max_iterations:
    i = i + 1
    result = fix_agent(next_prompt)
    print(result)

    actions = parse_actions(result)
    print(actions)
    execute_actions(actions)
    screenshot_path = "../screenshots/Screenshot (60).png"
    parsed_content, image_content = get_parsed_image_content(screenshot_path)
    next_prompt = f"Observation: {parsed_content}"
"""





