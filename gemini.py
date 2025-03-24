from vertexai.preview.generative_models import GenerativeModel
import vertexai

# Init Vertex AI (no API key needed!)
vertexai.init(project="gen-lang-client-0225271187", location="us-central1")

# Load Gemini Flash model
model = GenerativeModel("gemini-2.0-flash-001")

# Send a prompt
response = model.generate_content("Explain how AI works in a few words.")
print(response.text)