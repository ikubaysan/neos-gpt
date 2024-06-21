import requests
import json
from modules.helpers.logging_helper import logger
from modules.ConversationContainer import OpenAIConversationContainer
from modules.helpers.prompt_helpers import get_num_tokens_from_string
import logging

class OpenAIAPIClient:
    def __init__(self, base_url: str, path: str, api_key: str, max_conversation_tokens: int,
                 max_response_tokens: int, max_dialogues_per_conversation: int, conversation_prune_after_seconds: int,
                 temperature: float, system_message: str = None):
        self.base_url = base_url
        self.path = path
        self.api_key = api_key
        self.max_conversation_tokens = max_conversation_tokens
        self.max_response_tokens = max_response_tokens
        self.temperature = temperature
        self.system_message = system_message
        self.conversations = OpenAIConversationContainer(conversation_prune_after_seconds=conversation_prune_after_seconds,
                                                         max_dialogues_per_conversation=max_dialogues_per_conversation)

    def send_prompt(self, prompt: str, model: str, image_url: str = None, conversation_id: str = None) -> str:
        headers = {
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
        }

        messages = []
        conversation = None
        if self.system_message is not None:
            system_message_content = [{"type": "text", "text": self.system_message}]
            messages.append({"role": "system", "content": system_message_content})

        prompt_tokens = get_num_tokens_from_string(prompt, model)
        if conversation_id is None:
            # No conversation ID, so there is no context to add to the prompt
            pass
        else:
            conversation = self.conversations.get_conversation(conversation_id=conversation_id, model=model)
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

        logger.info(f"Using specified model: {model}")

        body = {
            "model": model,
            "messages": messages,
            "max_tokens": self.max_response_tokens,
            "temperature": self.temperature
        }

        logger.info(f"Sending API request to {self.path} with body: {body}")

        response = self.post(body=body, headers=headers, path=self.path)
        logger.info(f"Got response: {response}")
        response_json = json.loads(response)

        try:
            response_message = response_json["choices"][0]["message"]
        except:
            return response

        response_text = response_message["content"].strip()

        if conversation is not None:
            conversation.add(prompt_message=prompt_message, response_message=response_message)

        return response_text

    def post(self, body: dict, headers: dict, path: str):
        response = requests.post(self.base_url + path, headers=headers, data=json.dumps(body))
        return response.text


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    from modules.Config import Config
    config = Config('../config.ini')

    openai_api_client = OpenAIAPIClient(base_url=config.openai_base_url, path=config.openai_path,
                                        api_key=config.openai_api_key,
                                        max_conversation_tokens=config.openai_max_conversation_tokens,
                                        max_response_tokens=config.openai_max_response_tokens,
                                        max_dialogues_per_conversation=config.openai_max_dialogues_per_conversation,
                                        conversation_prune_after_seconds=config.openai_conversation_prune_after_seconds,
                                        temperature=config.openai_temperature, system_message=config.openai_system_message)

    model = config.openai_models[0]

    response = openai_api_client.send_prompt(prompt="What is the capital of France?", conversation_id="test", model=model)
    logger.info(f"Got response: {response}")
    response = openai_api_client.send_prompt(prompt="And Germany?", conversation_id="test", model=model)
    logger.info(f"Got response: {response}")
    response = openai_api_client.send_prompt(prompt="How about Spain?", conversation_id="test", model=model)
    logger.info(f"Got response: {response}")
    response = openai_api_client.send_prompt(prompt="Describe the image in 1 sentence without describing the thing the cat is lying on.",
                                             image_url="https://agentlegoodbye.com/wp-content/uploads/photo-gallery/thumb/Purrito-4.jpg",
                                             conversation_id="test", model=model)
    logger.info(f"Got response: {response}")
    response = openai_api_client.send_prompt(prompt="Now tell me the color of the thing the cat is lying on", conversation_id="test", model=model)
    logger.info(f"Got response: {response}")
