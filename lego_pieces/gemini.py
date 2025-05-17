from vertexai.preview.generative_models import GenerativeModel
import vertexai

# Init Vertex AI (no API key needed!)
vertexai.init(project="gen-lang-client-0225271187", location="us-central1")

# Load Gemini Flash model
model = GenerativeModel("gemini-2.5-flash-preview-04-17")

# Send a prompt
response = model.generate_content("Under which tab do you think column editor is in Notepad++ application?")
print(response.text)