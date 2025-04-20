# Third Party Libraries
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai

# Standard Library
import json
import os

# Custom Project Modules
from prompts import system_prompt, action_prompt, observation_prompt, reflexion_prompt, AVAILABLE_ACTIONS, EXAMPLE_RESPONSE
from env_manager import launch_notepadpp, capture_notepadpp_only
from action_manager import parse_actions, execute_actions
from omniparser import get_parsed_image_content
from util import clean_json_response


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
            parsed = json.loads(clean_json_response(result)) # Just in case LLM wraps the response around ```json ```
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
    
class ObserverAgent():
    def __init__(self, project_id="gen-lang-client-0225271187", location="us-central1"):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0,
                "response_mime_type": "application/json"
            }
        )
    
    def __call__(self, prompt="", screenshot_path=None):
        result = self.execute(prompt, screenshot_path)
        return result
    
    def execute(self, prompt, screenshot_path):
        if screenshot_path:
            with open(screenshot_path, "rb") as f:
                image_bytes = f.read()
            
            # Create the image part
            image_part = Part.from_data(data=image_bytes, mime_type="image/png")
            
            # Now pass the image and the combined text
            response = self.model.generate_content([
                image_part,
                prompt
            ])
        else:
            response = self.model.generate_content(self.messages)

        return response.text
    

def agent_loop(bug_report, max_iterations):

    os.makedirs("screenshots", exist_ok=True)

    launch_notepadpp()

    # STEP 1: Take initial screenshot
    initial_screenshot_path = f"screenshots/step_0.png"
    capture_notepadpp_only(initial_screenshot_path)

    # STEP 2: Parse the image
    parsed_content, image_content = get_parsed_image_content(initial_screenshot_path)

    print(parsed_content)

    # STEP 3: Format the system prompt with bug report and parsed content
    formatted_prompt = system_prompt.format(
        available_actions = AVAILABLE_ACTIONS,
        bug_report=bug_report,
        parsed_content=json.dumps(parsed_content, indent=2),
        example_response = EXAMPLE_RESPONSE
    )

    # STEP 4: Create agent with full system prompt
    fix_agent = FixAgent(system=formatted_prompt)

    # STEP 5: Create reflection agent as well.
    reflection_agent = ReflectionAgent()  

    # STEP 6: Create an observer agent
    observer_agent = ObserverAgent()

    print(f"\n--- Iteration 0 ---")
    result = fix_agent()
    print(result)
    actions = parse_actions(result)
    # print(actions)
    execute_actions(actions)

    # STEP 7: Run loop with screenshot + observation each time
    for i in range(1, max_iterations + 1):
        print(f"\n--- Iteration {i} ---")

        # Step i.3: Take new screenshot
        screenshot_path = f"screenshots/step_{i}.png"
        capture_notepadpp_only(screenshot_path)

        # Step i.4: Parse screenshot
        parsed_content, image_content = get_parsed_image_content(screenshot_path)

        # Step i.5: Observe the screen
        formatted_observation_prompt = observation_prompt.format(
            bug_report = bug_report
            # parsed_content = json.dumps(parsed_content, indent = 2)
        )

        ui_description = observer_agent(formatted_observation_prompt, screenshot_path)

        print(f"UI DESCRIPTION: {ui_description}")

        # Step i.6: Reflexion evaluation
        formatted_reflexion_prompt = reflexion_prompt.format(
            available_actions = AVAILABLE_ACTIONS,
            bug_report=bug_report,
            trajectory=json.dumps(fix_agent.trajectory, indent=2),
            parsed_content=json.dumps(parsed_content, indent=2),
            ui_description=ui_description
        )

        reflection_output = reflection_agent(formatted_reflexion_prompt, screenshot_path)
        print("Reflection Output:\n", reflection_output)

        # Step i.7: Update with new observation
        formatted_action_prompt = action_prompt.format(
            bug_report = bug_report,
            trajectory=json.dumps(fix_agent.trajectory, indent=2),
            reflection=reflection_output,
            parsed_screenshot=json.dumps(parsed_content, indent=2),
            ui_description = ui_description,
            available_actions = AVAILABLE_ACTIONS,
            example_response = EXAMPLE_RESPONSE
        )        
        result = fix_agent(formatted_action_prompt, screenshot_path)
        print(result)
        actions = parse_actions(result)
        # print(actions)
        execute_actions(actions)


# bug_report = "STR: Make sure no text is selected. Edit -> Paste Special -> Copy Binary Content . Result: NPP crashes."
bug_report = r"""Steps to Reproduce:
Paste a└c into an empty Notepad++ tab.
Open the Find dialog, set Search Mode: Regular expression, and Find what: (?-i)\u*(?=[^\l]).
Click Count.
"""

agent_loop(bug_report=bug_report, max_iterations=19)

click_green_arrows_prompt = """
You are reproducing a Notepad++ bug. You are given the current screen as an image separately.

Your task is to identify **green triangle fold markers** in the image (these are the markers used to hide or show folded lines of text).

---

INSTRUCTIONS:
- Carefully observe the screenshot image and its parsed contents.
- Locate any **green triangle icons** (used for hiding/showing folded lines).
- Use `moveTo` and `click` actions to interact with them.
- Respond ONLY with a JSON object containing:
  - `thought`: your reasoning
  - `actions`: one or more PyAutoGUI-compatible actions
- They are between Line number and the actual text in the line. Adjust the bbox accordingly.
- Just click only one of them.

{parsed_content}


---

EXAMPLE OUTPUT:
{{
  "thought": "I see a green triangle on the left margin, which is a fold marker. I will move to it and click.",
  "actions": [
    {{"type": "moveTo", "bbox": [0.015, 0.22, 0.04, 0.25]}},
    {{"type": "click"}}
  ]
}}
"""





