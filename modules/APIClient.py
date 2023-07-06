import requests
import json
import time
import tiktoken
from modules.helpers.logging_helper import logger

class Dialogue:
    def __init__(self, prompt: str, response: str, model: str):
        self.prompt = prompt
        self.response = response
        self.prompt_num_tokens = self.get_num_tokens_from_string(prompt, model)
        self.response_num_tokens = self.get_num_tokens_from_string(response, model)

    @staticmethod
    def get_num_tokens_from_string(string: str, encoding_name: str) -> int:
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens


class Conversation:
    # A circular buffer of prompts and their responses.
    # [0] would be the oldest prompt, [max_length - 1] would be the newest prompt
    def __init__(self, max_length: int):
        self.max_length = max_length
        self.update_epoch = time.time()
        self.prompts = []
        self.responses = []

    def add(self, prompt: str, response: str):
        if len(self.prompts) == self.max_length:
            self.prompts.pop(0)
            self.responses.pop(0)
        self.prompts.append(prompt)
        self.responses.append(response)
        self.update_epoch = time.time()

    def get_messages_for_api(self):
        # Return all prompts and responses in a format that can be sent to the API
        messages = []
        for i in range(len(self.prompts)):
            messages.append({"role": "user", "content": self.prompts[i]})
            messages.append({"role": "assistant", "content": self.responses[i]})
        return messages

class ConversationContainer:
    def __init__(self, conversation_prune_after_seconds: int, conversation_length: int):
        self.conversation_prune_after_seconds = conversation_prune_after_seconds
        self.conversation_length = conversation_length
        self.prompt_histories = {}

    def get_conversation(self, conversation_id: str) -> Conversation:
        if conversation_id not in self.prompt_histories:
            self.prompt_histories[conversation_id] = Conversation(max_length=self.conversation_length)
        return self.prompt_histories[conversation_id]

    def prune(self):
        # Remove prompt histories that have not been used in a while
        current_time = time.time()
        for conversation_id in list(self.prompt_histories):
            conversation = self.prompt_histories[conversation_id]
            if current_time - conversation.creation_epoch > self.conversation_prune_after_seconds:
                del self.prompt_histories[conversation_id]

class APIClient:
    def __init__(self, base_url: str, path: str, api_key: str, model: str, max_response_tokens: int,
                 conversation_length: int, conversation_prune_after_seconds: int, temperature: float,
                 system_message: str = None):
        self.base_url = base_url
        self.path = path
        self.api_key = api_key
        self.model = model
        self.max_response_tokens = max_response_tokens
        self.temperature = temperature
        self.system_message = system_message
        self.prompt_histories = ConversationContainer(conversation_prune_after_seconds=conversation_prune_after_seconds,
                                                      conversation_length=conversation_length)

    def send_prompt(self, prompt: str, conversation_id: str = None) -> str:
        headers = {
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
        }

        messages = []
        conversation = None
        if self.system_message is not None:
            messages.append({"role": "system", "content": self.system_message})

        if conversation_id is None:
            # No conversation ID, so there is no context to add to the prompt
            messages.append({"role": "user", "content": prompt})
        else:
            conversation = self.prompt_histories.get_conversation(conversation_id=conversation_id)
            previous_messages = conversation.get_messages_for_api()
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
        logger.info(f"Got response: {response}")
        response_json = json.loads(response)
        text = response_json["choices"][0]["message"]["content"].strip()

        if conversation is not None:
            conversation.add(prompt=prompt, response=text)

        return text

    def post(self, body: dict, headers: dict, path: str):
        response = requests.post(self.base_url + path, headers=headers, data=json.dumps(body))
        return response.text