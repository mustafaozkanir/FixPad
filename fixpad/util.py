# util class that contains auxiliary methods

# Loads the prompt from the txt file
def load_prompt(path="prompt.txt"):
    with open(path, "r") as f:
        return f.read()

# Replaces the placeholders in the prompt with the actual data
def fill_prompt(template, job_description, image, parsed_content):
    return template.format(
        bug_report=job_description,
        image=image,
        parsed_content=parsed_content
    )

"""
    Removes the first and last lines in the LLM output,
    if it is wrapped with wrappers like ``` to ease parsing.
"""
def clean_json_response(response_text):
    lines = response_text.strip().splitlines()
    
    if lines and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
        lines = lines[1:-1]

    return "\n".join(lines)
