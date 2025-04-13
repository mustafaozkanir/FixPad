import vertexai
from vertexai.preview.generative_models import GenerativeModel

from util import load_prompt, fill_prompt, clean_json_response
from omniparser import get_parsed_image_content 
from fixpad.action_manager_old import execute_actions, parse_actions


def call_gemini(prompt_text):
    model = GenerativeModel("gemini-2.0-flash-001")
    response = model.generate_content(prompt_text)
    return response.text

# --- Your Inputs (replace with real data later) ---

job_description = "Restore the application window."

mock_image = "mock_image" # Currently the image is just a string
mock_parsed_content, mock_image = get_parsed_image_content("../screenshots/screenshot.png")

# --- Run the Agent ---

vertexai.init(project="gen-lang-client-0225271187", location="us-central1")

template = load_prompt()
filled_prompt = fill_prompt(template, job_description, mock_image, mock_parsed_content)

print("\n📨 Prompt sent to Gemini:")
print(filled_prompt)

response_text = call_gemini(filled_prompt)

print("\n📨 Raw LLM Output:")
print(response_text)

actions = parse_actions(response_text)

execute_actions(actions)
