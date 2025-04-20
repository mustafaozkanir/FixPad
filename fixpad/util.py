# Util class that contains auxiliary methods

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
