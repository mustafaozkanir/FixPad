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

image_base64 = parsed_data['processed_image']

# Decode the image
image_data = base64.b64decode(image_base64)

# Write to a PNG file
"""
with open("screenshots/annotated_screenshot.png", "wb") as f:
    f.write(image_data)

print("Saved: screenshots/annotated_screenshot.png")
"""

print(parsed_data)