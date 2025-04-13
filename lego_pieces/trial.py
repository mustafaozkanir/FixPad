from vertexai.preview.generative_models import GenerativeModel
import vertexai
import json

import requests
import os
import base64


api_key = os.getenv("INFERENCE_API_KEY_OMNIPARSER")


with open('../screenshots/screenshot.png', 'rb') as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

response = requests.post(
    'https://omniparser.inferenceapis.com/parse',
    json={'base64_image': image_data},
    headers=headers
)

parsed_data = response.json()

# ✅ Initialize Vertex AI
vertexai.init(project="gen-lang-client-0225271187", location="us-central1")

# ✅ Load Gemini Flash
model = GenerativeModel("gemini-2.0-flash-001")

# ✅ Define function to ask the LLM
def decide_action(ui_json, goal):
    prompt = f"""
                You are a UI agent.

                You will receive a list of UI elements detected in a screenshot (in JSON format), and a goal to accomplish.

                Each UI element includes:
                - text: label or name (e.g., "Replace")
                - coordinates: bounding box [left, top, right, bottom]

                Respond with the most appropriate action in **this JSON format**:

                [
                {{
                    "action": "click",
                    "target": "Replace",
                    "coordinates": [0.5351152420043945, 0.08042865991592407, 0.5507508516311646, 0.11287731677293777]
                }}
                ]

                Do NOT include any explanations or extra text — only return the JSON.

                --- UI ELEMENTS ---
                {json.dumps(ui_json, indent=2)}

                --- GOAL ---
                {goal}
            """

    response = model.generate_content(prompt)
    return response.text.strip()

goal = "Identify the next action to open a New Page which is an option inside File menu."

result = decide_action(parsed_data, goal)
print("LLM output:\n", result)

# ✅ Optional: try parsing as JSON
try:
    actions = json.loads(result)
    print("Parsed action:", actions[0])
except Exception as e:
    print("⚠️ Failed to parse JSON:", e)
