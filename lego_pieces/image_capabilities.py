# Result: gemini-2.0-flash-001 this modal is capable of understanding images


from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai

import base64
import PIL.Image

from fixpad.omniparser import get_parsed_image_content

vertexai.init(project="gen-lang-client-0225271187", location="us-central1")

model = GenerativeModel("gemini-2.0-flash-001")

#image = PIL.Image.open("screenshots/screenshot.png")
#image_part = Part.from_image(image)

#detected_elements, i= get_parsed_image_content("screenshots/screenshot.png")

prompt = f"""
            Describe what you see in the following image:

            """

# Load image and convert it to bytes
image_path = "screenshots/screenshot.png"
with open(image_path, "rb") as f:
    image_bytes = f.read()

# Create Part from raw image data
image_part = Part.from_data(data=image_bytes, mime_type="image/png")

# Ask Gemini with image + prompt
response = model.generate_content([
    image_part,
    "Describe what you see in this screenshot. "
])

print(response.text)

