import google.generativeai as genai
import time
import logging

logger = logging.getLogger(__name__)

class GoogleAIAPIClient:
    def __init__(self, api_key: str, model_name: str, json_response: bool = False):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)

        if json_response:
            self.model = genai.GenerativeModel(model_name=model_name,
                                               generation_config={"response_mime_type": "application/json"})
        else:
            self.model = genai.GenerativeModel(model_name=model_name)
        logger.info(f"Google AI API client initialized with model {model_name}")
        return

    def send_prompt(self, prompt: str) -> str:
        logger.info(f"Sending prompt to Google AI API with model {self.model_name}: '{prompt[:50]}...'")
        attempt_count = 0
        while True:
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text
            except Exception as e:
                logger.error(f"An error occurred while sending prompt to Google AI API: {e}")
                attempt_count += 1
                if attempt_count > 3:
                    return None
                time.sleep(10)
            else:
                break
        return response_text