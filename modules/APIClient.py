import requests
import json
import time
import tiktoken
from typing import List
from modules.helpers.logging_helper import logger

def get_num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

class Dialogue:
    def __init__(self, prompt_message: dict, response_message: dict, model: str):
        self.prompt_message = prompt_message
        self.prompt_text = prompt_message["content"][0]["text"].strip()
        self.response_message = response_message
        self.response_text = response_message["content"].strip()
        self.prompt_num_tokens = get_num_tokens_from_string(self.prompt_text, model)
        self.response_num_tokens = get_num_tokens_from_string(self.response_text, model)
        self.total_num_tokens = self.prompt_num_tokens + self.response_num_tokens


class Conversation:
    def __init__(self, max_length: int, model: str):
        self.max_length = max_length
        self.update_epoch = time.time()
        self.dialogues: List[Dialogue] = []
        self.model = model

    def add(self, prompt_message: dict, response_message: dict):
        dialogue = Dialogue(prompt_message, response_message, self.model)
        if len(self.dialogues) == self.max_length:
            self.dialogues.pop(0)
        self.dialogues.append(dialogue)
        self.update_epoch = time.time()

    def get_messages_for_api(self):
        messages = []
        for dialogue in self.dialogues:
            messages.append(dialogue.prompt_message)
            messages.append(dialogue.response_message)
        return messages

    def get_total_tokens(self):
        return sum([dialogue.total_num_tokens for dialogue in self.dialogues])

    def trim(self, prompt_tokens: int, token_limit: int):
        # Remove dialogues until the total number of the prompt and saved dialogues is less than the token limit
        while len(self.dialogues) > 0 and self.get_total_tokens() + prompt_tokens >= token_limit:
            self.dialogues.pop(0)


class ConversationContainer:
    def __init__(self, conversation_prune_after_seconds: int, max_dialogues_per_conversation: int, model: str):
        self.conversation_prune_after_seconds = conversation_prune_after_seconds
        self.max_dialogues_per_conversation = max_dialogues_per_conversation
        self.conversations = {}
        self.model = model

    def get_conversation(self, conversation_id: str) -> Conversation:
        if conversation_id not in self.conversations:
            # Create a new conversation if it doesn't exist
            self.conversations[conversation_id] = Conversation(max_length=self.max_dialogues_per_conversation, model=self.model)
        return self.conversations[conversation_id]

class APIClient:
    def __init__(self, base_url: str, path: str, api_key: str, model: str, max_conversation_tokens: int,
                 max_response_tokens: int, max_dialogues_per_conversation: int, conversation_prune_after_seconds: int,
                 temperature: float, system_message: str = None):
        self.base_url = base_url
        self.path = path
        self.api_key = api_key
        self.model = model
        self.max_conversation_tokens = max_conversation_tokens
        self.max_response_tokens = max_response_tokens
        self.temperature = temperature
        self.system_message = system_message
        self.conversations = ConversationContainer(conversation_prune_after_seconds=conversation_prune_after_seconds,
                                                      max_dialogues_per_conversation=max_dialogues_per_conversation,
                                                      model=model)

    def send_prompt(self, prompt: str, image_url: str = None, conversation_id: str = None, model: str = None) -> str:
        headers = {
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
        }

        messages = []
        conversation = None
        if self.system_message is not None:
            system_message_content = [{"type": "text", "text": self.system_message}]
            messages.append({"role": "system", "content": system_message_content})

        prompt_tokens = get_num_tokens_from_string(prompt, self.model)
        if conversation_id is None:
            # No conversation ID, so there is no context to add to the prompt
            pass
        else:
            conversation = self.conversations.get_conversation(conversation_id=conversation_id)
            conversation.trim(prompt_tokens=prompt_tokens, token_limit=self.max_conversation_tokens)
            previous_messages = conversation.get_messages_for_api()
            # Add the previous prompts and responses to the message list
            for message in previous_messages:
                messages.append(message)

        # Finally, add the new prompt
        prompt_content_list = []
        prompt_content_list.append({"type": "text", "text": prompt})
        if image_url:
            prompt_content_list.append({"type": "image_url", "image_url": {"url": image_url}})
        prompt_message = {"role": "user", "content": prompt_content_list}
        messages.append(prompt_message)

        if model is not None:
            logger.info(f"Using specified model: {model}")
        else:
            logger.info(f"Using default model: {self.model}")

        body = {
            "model": model if model is not None else self.model,
            "messages": messages,
            "max_tokens": self.max_response_tokens,
            "temperature": self.temperature
        }

        logger.info(f"Sending API request to {self.path} with body: {body}")

        response = self.post(body=body, headers=headers, path=self.path)
        logger.info(f"Got response: {response}")
        response_json = json.loads(response)
        response_message = response_json["choices"][0]["message"]
        response_text = response_message["content"].strip()

        if conversation is not None:
            conversation.add(prompt_message=prompt_message, response_message=response_message)

        return response_text

    def post(self, body: dict, headers: dict, path: str):
        response = requests.post(self.base_url + path, headers=headers, data=json.dumps(body))
        return response.text