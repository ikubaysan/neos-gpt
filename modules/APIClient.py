import requests
import json
from modules.helpers.logging_helper import logger


class PromptHistory:
    # A circular buffer of prompts and their responses.
    # [0] would be the oldest prompt, [max_length - 1] would be the newest prompt
    def __init__(self, max_length: int):
        self.max_length = max_length
        self.prompts = []
        self.responses = []

    def add(self, prompt: str, response: str):
        if len(self.prompts) == self.max_length:
            self.prompts.pop(0)
            self.responses.pop(0)
        self.prompts.append(prompt)
        self.responses.append(response)

    def get_messages_for_api(self):
        # Return all prompts and responses in a format that can be sent to the API
        messages = []
        for i in range(len(self.prompts)):
            messages.append({"role": "user", "content": self.prompts[i]})
            messages.append({"role": "assistant", "content": self.responses[i]})
        return messages


class APIClient:
    def __init__(self, base_url: str, path: str, api_key: str, model: str, max_response_tokens: int, prompt_history_length:int, temperature: float, system_message: str):
        self.base_url = base_url
        self.path = path
        self.api_key = api_key
        self.model = model
        self.max_response_tokens = max_response_tokens
        self.temperature = temperature
        self.system_message = system_message
        self.prompt_history = PromptHistory(max_length=prompt_history_length)

    def send_prompt(self, prompt: str) -> str:
        headers = {
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
        }

        messages = []
        if len(self.system_message) > 0:
            messages.append({"role": "system", "content": self.system_message})

        previous_messages = self.prompt_history.get_messages_for_api()
        # Add the previous prompts and responses to the message list
        for message in previous_messages:
            messages.append(message)
        # Finally, add the new prompt
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_response_tokens,
            "temperature": self.temperature
        }

        logger.info(f"Sending API request to {self.path} with body: {body}")

        response = self.post(body=body, headers=headers, path=self.path)
        response_json = json.loads(response)
        text = response_json["choices"][0]["message"]["content"].strip()
        self.prompt_history.add(prompt=prompt, response=text)
        return text

    def post(self, body: dict, headers: dict, path: str):
        response = requests.post(self.base_url + path, headers=headers, data=json.dumps(body))
        return response.text