import vertexai
from vertexai.preview.generative_models import GenerativeModel

import pyautogui as py
import json
import os
from datetime import datetime

from prompts import system_prompt, observation_prompt
from omniparser import get_parsed_image_content
from action_manager import parse_actions, execute_actions

import subprocess
import time
import pygetwindow as gw

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
        if system is not None:
            self.messages.append(f"SYSTEM: {system}")

    def __call__(self, message=""):
        if message:
            self.messages.append(f"USER: {message}")
        
        result = self.execute()
        
        self.messages.append(f"ASSISTANT: {result}")
        return result

    def execute(self):
        # Build full prompt including prior messages and the latest screen state
        #full_prompt = "\n\n".join(self.messages + [self.latest_observation])
        response = self.model.generate_content(self.messages)
        all_input = "\n".join(self.messages)
        #check_token_budget(all_input)
        # print(full_prompt)
        return response.text
    
    
def main():
    fix_agent = FixAgent(system=system_prompt)
    screenshot_path = "../screenshots/screenshot.png"

    # Update agent with parsed UI from screenshot
    fix_agent.observe(screenshot_path)

    result = fix_agent()
    print(result)
"""
    result = fix_agent()
    print(result)

    screenshot_path = "../screenshots/Screenshot (60).png"
    parsed_content, image_content = get_parsed_image_content(screenshot_path)
    next_prompt = f"Observation: {parsed_content}"

    result = fix_agent(next_prompt)
    print(result)
    #print(fix_agent.messages)
"""
    #py.moveTo(18, 30)
    #py.click()

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
        bug_report=bug_report,
        image=initial_screenshot_path,
        parsed_content=json.dumps(parsed_content, indent=2)
    )

    # STEP 4: Create agent with full system prompt
    fix_agent = FixAgent(system=formatted_prompt)

    # STEP 5: Run loop with screenshot + observation each time
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


        # Step i.5: Update with new observation
        formatted_observation_prompt = observation_prompt.format(
            bug_report = bug_report,
            image=screenshot_path,
            parsed_content=json.dumps(parsed_content, indent=2)
        )        
        fix_agent(formatted_observation_prompt)


# bug_report = "STR: Make sure no text is selected. Edit -> Paste Special -> Binary Content Copy. Result: NPP crashes."
bug_report = "STR: Paste the following lines in a new document. " 
"Test "
"Test "
"Test "
"Test "
"Test "
"Place the caret at line 3. View -> Hide Lines. Place the caret at line 2.View -> Hide Lines. Click on the show-lines markers. Click on the single show-lines marker."

agent_loop(bug_report=bug_report, max_iterations=4)




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





