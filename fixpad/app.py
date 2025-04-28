# Standard Library
import json, time, os

# Custom Project Modules
from prompts import system_prompt, action_prompt, observation_prompt, reflection_prompt, AVAILABLE_ACTIONS, EXAMPLE_RESPONSE
from env_manager import launch_notepadpp, capture_notepadpp_only, detect_crash, save_annotated_image
from util import clean_json_response, init_vertex_ai, log_parsed_content, log_messages
from agents import ActionAgent, ReflectionAgent, ObserverAgent
from action_manager import parse_actions, execute_actions
from omniparser import get_parsed_image_content

init_vertex_ai()

def agent_loop(bug_report, max_iterations):

    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("annotated_screenshots", exist_ok=True)

    launch_notepadpp()

    initial_screenshot_path = f"screenshots/iteration_0.png"
    capture_notepadpp_only(initial_screenshot_path)

    parsed_content, image_content = get_parsed_image_content(initial_screenshot_path)
    
    log_parsed_content(parsed_content, 0)

    annotated_screenshot_path = f"annotated_screenshots/iteration_0.png"
    save_annotated_image(image_content, annotated_screenshot_path)

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
    log_messages(result, "Action Agent", 0)
    actions = parse_actions(result)
    execute_actions(actions)

    for i in range(1, max_iterations + 1):
        
        print(f"\n--- Iteration {i} ---")

        screenshot_path = f"screenshots/iteration_{i}.png"
        capture_notepadpp_only(screenshot_path)

        parsed_content, image_content = get_parsed_image_content(screenshot_path)

        log_parsed_content(parsed_content, i)

        annotated_screenshot_path = f"annotated_screenshots/iteration_{i}.png"
        save_annotated_image(image_content, annotated_screenshot_path)
        
        # print(parsed_content) # DEBUGGING LINE

        formatted_observation_prompt = observation_prompt.format(
            bug_report = bug_report
            # parsed_content = json.dumps(parsed_content, indent = 2)
        )

        ui_description = observer_agent(formatted_observation_prompt, screenshot_path)

        print(f"Observation: {ui_description}")
        log_messages(result, "Observation Agent", i)

        formatted_reflection_prompt = reflection_prompt.format(
            available_actions = AVAILABLE_ACTIONS,
            bug_report=bug_report,
            trajectory=json.dumps(action_agent.trajectory, indent=2),
            parsed_content=json.dumps(parsed_content, indent=2),
            ui_description=ui_description
        )

        reflection_output = reflection_agent(formatted_reflection_prompt, screenshot_path)
        print("Reflection:\n", reflection_output)
        log_messages(result, "Reflection Agent", -1)

        formatted_action_prompt = action_prompt.format(
            parsed_screenshot=json.dumps(parsed_content, indent=2),
            ui_description = ui_description,
            trajectory=json.dumps(action_agent.trajectory, indent=2),
            bug_report = bug_report,
            reflection=reflection_output,
            example_response = EXAMPLE_RESPONSE,
            available_actions = AVAILABLE_ACTIONS
        )        

        result = action_agent(formatted_action_prompt, screenshot_path)
        print(result)
        log_messages(result, "Action Agent", -1)
        actions = parse_actions(result)
        execute_actions(actions)

        time.sleep(3) # To not crash Gemini Server
        """
        if(detect_crash()):
            print("✅ Bug is successfully reproduced!")
            break
        """

bug_report="""
Steps To Reproduce
1/ Download a Notepad++ Portable Minimalist version to ensure there are no unwanted plugins.

2/ Extract it.

3/ Launch Notepad++

4/ Write the following lines:

{
	// sample
	// sample
}
{
	// sample
	// sample
}
5/ Highlight the last 4 lines (lines 8 to 5) and press ALT + H to hide them.

6/ Now, you should only see this:

{
	// sample
	// sample
}
}
With the fold markers on line 4 (>) and line 8 (<).


7/ Highlight all 5 lines (lines 8 to 1, including lines 5, 6, and 7, which are hidden) and press ALT + H to hide them.


8/ Notepad++ freezes.


Current Behavior
Notepad++ Freeze.
"""

agent_loop(bug_report=bug_report, max_iterations=30)