import time
import logging
from modules.helpers.network_helpers import get_image_from_url, get_base64_from_image_url
from modules.ConversationContainer import ClaudeConversationContainer
import PIL.Image
import anthropic

logger = logging.getLogger(__name__)

class ClaudeAPIClient:
    def __init__(self, api_key: str, model_name: str, conversation_prune_after_seconds: int,
                 max_dialogues_per_conversation: int, json_response: bool = False):
        self.api_key = api_key
        self.model_name = model_name

        self.conversations = ClaudeConversationContainer(conversation_prune_after_seconds=conversation_prune_after_seconds,
                                                   max_dialogues_per_conversation=max_dialogues_per_conversation,
                                                   model=model_name)

        self.model = anthropic.Anthropic(api_key=api_key)

        logger.info(f"Claude API client initialized with model {model_name}")
        return

    def send_prompt(self, prompt: str, image_url: str = None, conversation_id: str = None) -> str:
        logger.info(f"Sending prompt to Claude API with model {self.model_name}: '{prompt[:50]}...'")

        conversation = None
        messages = []

        if conversation_id is None:
            # No conversation ID, so there is no context to add to the prompt
            pass
        else:
            conversation = self.conversations.get_conversation(conversation_id=conversation_id, model=self.model_name)
            previous_messages = conversation.get_messages_for_api()
            # Add the previous prompts and responses to the message list
            for message in previous_messages:
                messages.append(message)

        if len(prompt) == 0 and not image_url:
            return "Prompt is empty and no image was provided"

        if len(prompt) > 0:
            outbound_parts = [{
                "type": "text",
                "text": prompt
            }]
        else:
            outbound_parts = []

        if image_url:

            image_file_extension = image_url.split(".")[-1]

            outbound_parts.append(
                {
                    "type": "image",
                    "source":
                        {

                            "type": "base64",
                            "media_type": f"image/{image_file_extension}",
                            "data": get_base64_from_image_url(image_url)
                        }
                }
            )

        new_user_message = {'role': 'user',
                            'content': outbound_parts}
        messages.append(new_user_message)

        response = self.model.messages.create(
            model=self.model_name,
            max_tokens=1024,
            messages=messages)

        response_text = ""
        for response_content in response.content:
            response_text += response_content.text

        if conversation is not None:
            conversation.add(prompt_contents=new_user_message, response_text=response_text)

        return response_text


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    from modules.Config import Config
    config = Config('../config.ini')

    claude_api_client = ClaudeAPIClient(api_key=config.claude_api_key,
                      model_name=config.claude_model,
                      conversation_prune_after_seconds=config.openai_conversation_prune_after_seconds,
                      max_dialogues_per_conversation=config.openai_max_dialogues_per_conversation)

    #response = google_api_client.send_prompt(prompt="Describe the image", image_url="https://agentlegoodbye.com/wp-content/uploads/photo-gallery/thumb/Purrito-4.jpg")
    #logger.info(f"Got response: {response}")

    response = claude_api_client.send_prompt(prompt="What model are you? What is the capital of France?", conversation_id="test")
    logger.info(f"Got response: {response}")
    # response = google_api_client.send_prompt(prompt="And Germany?", conversation_id="test")
    # logger.info(f"Got response: {response}")
    # response = google_api_client.send_prompt(prompt="How about Spain?", conversation_id="test")
    # logger.info(f"Got response: {response}")

    response = claude_api_client.send_prompt(prompt="Describe the image in 1 sentence without describing the thing the cat is lying on.",
                                             image_url="https://agentlegoodbye.com/wp-content/uploads/photo-gallery/thumb/Purrito-4.jpg",
                                             conversation_id="test")

    logger.info(f"Got response: {response}")
    response = claude_api_client.send_prompt(prompt="Now tell me the color of the thing the cat is lying on", conversation_id="test")
    logger.info(f"Got response: {response}")


    response = claude_api_client.send_prompt(prompt="What were the last things we spoke about?", conversation_id="test2")
    logger.info(f"Got response: {response}")
    pass