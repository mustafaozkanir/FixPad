import requests
import os
import base64


api_key = os.getenv("INFERENCE_API_KEY_OMNIPARSER");



with open('screenshots/screenshot.png', 'rb') as image_file:
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

print(parsed_data)