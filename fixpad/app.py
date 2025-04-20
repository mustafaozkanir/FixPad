# Standard Library
import json
import os

# Custom Project Modules
from prompts import system_prompt, action_prompt, observation_prompt, reflexion_prompt, AVAILABLE_ACTIONS, EXAMPLE_RESPONSE
from env_manager import launch_notepadpp, capture_notepadpp_only
from action_manager import parse_actions, execute_actions
from omniparser import get_parsed_image_content
from util import clean_json_response, init_vertex_ai
from agents import ActionAgent, ReflectionAgent, ObserverAgent

init_vertex_ai()

def agent_loop(bug_report, max_iterations):

    os.makedirs("screenshots", exist_ok=True)

    launch_notepadpp()

    initial_screenshot_path = f"screenshots/iteration_0.png"
    capture_notepadpp_only(initial_screenshot_path)

    parsed_content, image_content = get_parsed_image_content(initial_screenshot_path)

    # print(parsed_content) # DEBUGGING LINE

    formatted_prompt = system_prompt.format(
        available_actions = AVAILABLE_ACTIONS,
        bug_report=bug_report,
        parsed_content=json.dumps(parsed_content, indent=2),
        example_response = EXAMPLE_RESPONSE
    )

    action_agent = ActionAgent(system=formatted_prompt)

    reflection_agent = ReflectionAgent()

    observer_agent = ObserverAgent()

    print(f"\n--- Iteration 0: Invoke the Agent via System Prompt ---")
    result = action_agent(message="", screenshot_path=initial_screenshot_path)
    print(result)
    actions = parse_actions(result)
    execute_actions(actions)

    for i in range(1, max_iterations + 1):
        
        print(f"\n--- Iteration {i} ---")

        screenshot_path = f"screenshots/iteration_{i}.png"
        capture_notepadpp_only(screenshot_path)

        parsed_content, image_content = get_parsed_image_content(screenshot_path)

        formatted_observation_prompt = observation_prompt.format(
            bug_report = bug_report
            # parsed_content = json.dumps(parsed_content, indent = 2)
        )

        ui_description = observer_agent(formatted_observation_prompt, screenshot_path)

        print(f"Observation: {ui_description}")

        formatted_reflexion_prompt = reflexion_prompt.format(
            available_actions = AVAILABLE_ACTIONS,
            bug_report=bug_report,
            trajectory=json.dumps(action_agent.trajectory, indent=2),
            parsed_content=json.dumps(parsed_content, indent=2),
            ui_description=ui_description
        )

        reflection_output = reflection_agent(formatted_reflexion_prompt, screenshot_path)
        print("Reflection:\n", reflection_output)

        formatted_action_prompt = action_prompt.format(
            bug_report = bug_report,
            trajectory=json.dumps(action_agent.trajectory, indent=2),
            reflection=reflection_output,
            parsed_screenshot=json.dumps(parsed_content, indent=2),
            ui_description = ui_description,
            available_actions = AVAILABLE_ACTIONS,
            example_response = EXAMPLE_RESPONSE
        )        

        result = action_agent(formatted_action_prompt, screenshot_path)
        print(result)
        actions = parse_actions(result)
        execute_actions(actions)


bug_report = r"""Steps to Reproduce:
Paste a└c into an empty Notepad++ tab.
Open the Find dialog, set Search Mode: Regular expression, and Find what: (?-i)\u*(?=[^\l]).
Click Count.
"""

agent_loop(bug_report=bug_report, max_iterations=15)

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





