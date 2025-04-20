# Util class that contains auxiliary methods

# Third Party Libraries
import vertexai

# Standard Library
import os
import json

def init_vertex_ai():
    # Get project id and location from .env
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION")

    # Initialize Vertex AI globally once
    vertexai.init(project=project_id, location=location)

"""
    Removes the first and last lines in the LLM output,
    if it is wrapped with wrappers like ``` to ease parsing.
    
    This is a further precaution as LLMs sometimes but not always
    wraps it response around ```json ```
"""
def clean_json_response(response_text):
    lines = response_text.strip().splitlines()
    
    if lines and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
        lines = lines[1:-1]

    return "\n".join(lines)

def log_parsed_content(parsed_content, iteration, file_path="parsed_content_log.txt"):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n------ Iteration {iteration} ------\n")
        f.write(json.dumps(parsed_content, indent=2))
        f.write("\n")

