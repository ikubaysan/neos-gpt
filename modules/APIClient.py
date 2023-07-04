import requests
import json
from modules.helpers.logging_helper import logger

class APIClient:
    def __init__(self, base_url: str, path: str, api_key: str, model: str, max_response_tokens: int, temperature: float):
        self.base_url = base_url
        self.path = path
        self.api_key = api_key
        self.model = model
        self.max_response_tokens = max_response_tokens
        self.temperature = temperature



    def send_prompt(self, prompt: str) -> str:
        headers = {
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
        }

        body = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": self.max_response_tokens,
            "temperature": self.temperature
        }

        response = self.post(body=body, headers=headers, path=self.path)
        response_json = json.loads(response)
        if "choices" not in response_json:
            raise ValueError(f"Error - choices not found in response_json. Response: {response_json}")
        text = response_json["choices"][0]["text"].strip()
        return text

    def post(self, body: dict, headers: dict, path: str):
        response = requests.post(self.base_url + path, headers=headers, data=json.dumps(body))
        return response.text