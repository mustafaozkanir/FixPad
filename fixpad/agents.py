# Third Party Libraries
from vertexai.preview.generative_models import GenerativeModel, Part

# Standard Library
import json

# Custom Project Modules
from util import clean_json_response

class BaseAgent:
    def __init__(self, memory_enabled=True, model_name="gemini-2.0-flash"):
        self.memory_enabled = memory_enabled
        self.messages = [] if memory_enabled else None

        self.model = GenerativeModel(model_name = model_name,
                                     generation_config={
                                        "temperature": 0,
                                        "response_mime_type": "application/json"
                                        }
                                     )
        
    def add_message(self, role, content):
        if self.memory_enabled:
            self.messages.append(f"{role}: {content}")

    def execute(self, prompt="", screenshot_path=None):
        if screenshot_path:
            with open(screenshot_path, "rb") as f:
                image_bytes = f.read()
            image_part = Part.from_data(data=image_bytes, mime_type="image/png")
            
            if self.memory_enabled and isinstance(self.messages, list):
                text_prompt = "\n".join(self.messages)
            else:
                text_prompt = prompt

            response = self.model.generate_content([image_part, text_prompt])
        else:
            prompt_to_send = "\n".join(self.messages) if self.memory_enabled else prompt
            response = self.model.generate_content(prompt_to_send)

        return response.text

class ActionAgent(BaseAgent):
    def __init__(self, system=None):
        super().__init__(memory_enabled=True)
        self.trajectory = []
        if system is not None:
            self.add_message("SYSTEM", system)

    def __call__(self, message="", screenshot_path=None):
        if message:
            self.add_message("USER", message)
        
        result = self.execute(screenshot_path)
        self.maintain_trajectory(result)
        self.add_message("ASSISTANT", result)
        return result

    def maintain_trajectory(self, result):
        try:
            parsed = json.loads(clean_json_response(result))
            thought = parsed.get("thought", "")
            actions = parsed.get("actions", [])
            if thought and isinstance(actions, list):
                self.trajectory.append({"thought": thought, "actions": actions})
        except Exception as e:
            print("Failed to parse thought/action for trajectory:", e)


    def maintain_trajectory(self, result):
        try:
            # Just in case LLM wraps the response around ```json ```
            parsed = json.loads(clean_json_response(result))
            thought = parsed.get("thought", "")
            actions = parsed.get("actions", [])
            if thought and isinstance(actions, list):
                self.trajectory.append({"thought": thought, "actions": actions})
        except Exception as e:
            print("Failed to parse thought/action for trajectory:", e)

class ReflectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(memory_enabled=True)

    def __call__(self, message="", screenshot_path=None):
        if message:
            self.add_message("USER", message)

        result = self.execute(screenshot_path)
        self.add_message("ASSISTANT", result)
        return result
    
class ObserverAgent(BaseAgent):
    def __init__(self):
        super().__init__(memory_enabled=False)

    def __call__(self, prompt="", screenshot_path=None):
        return self.execute(prompt, screenshot_path)