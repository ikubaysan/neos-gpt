import google.generativeai as genai
import time
import logging
from modules.helpers.network_helpers import get_image_from_url
from modules.ConversationContainer import GoogleConversationContainer
import PIL.Image

logger = logging.getLogger(__name__)

class GoogleAIAPIClient:
    def __init__(self, api_key: str, model_name: str, conversation_prune_after_seconds: int,
                 max_dialogues_per_conversation: int, json_response: bool = False):
        self.api_key = api_key
        self.model_name = model_name

        # See:
        # https://stackoverflow.com/a/78078401/8151234
        # https://ai.google.dev/gemini-api/docs/safety-settings
        # These are the 4 safety categories, and default threshold is "BLOCK_MEDIUM_AND_ABOVE". Let's disable them.
        self.safe = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            }
        ]

        self.conversations = GoogleConversationContainer(conversation_prune_after_seconds=conversation_prune_after_seconds,
                                                   max_dialogues_per_conversation=max_dialogues_per_conversation,
                                                   model=model_name)

        genai.configure(api_key=api_key)

        if json_response:
            self.model = genai.GenerativeModel(model_name=model_name,
                                               generation_config={"response_mime_type": "application/json"})
        else:
            self.model = genai.GenerativeModel(model_name=model_name)
        logger.info(f"Google AI API client initialized with model {model_name}")
        return

    def send_prompt(self, prompt: str, image_url: str = None, conversation_id: str = None) -> str:
        logger.info(f"Sending prompt to Google AI API with model {self.model_name}: '{prompt[:50]}...'")

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

        outbound_parts = []
        if image_url:
            image = get_image_from_url(image_url)
            if image is None:
                return f"Failed to download image from {image_url}"
            outbound_parts.append(image)

        outbound_parts.append(prompt)

        new_user_message = {'role': 'user',
                            'parts': outbound_parts}
        messages.append(new_user_message)

        response = self.model.generate_content(messages, safety_settings=self.safe)

        response_text = response.text

        if conversation is not None:
            conversation.add(prompt_contents=new_user_message, response_text=response_text)

        return response_text


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    from modules.Config import Config
    config = Config('../config.ini')

    google_api_client = GoogleAIAPIClient(api_key=config.google_api_key,
                                          model_name=config.google_model,
                                          conversation_prune_after_seconds=config.openai_conversation_prune_after_seconds,
                                          max_dialogues_per_conversation=config.openai_max_dialogues_per_conversation)

    #response = google_api_client.send_prompt(prompt="Describe the image", image_url="https://agentlegoodbye.com/wp-content/uploads/photo-gallery/thumb/Purrito-4.jpg")
    #logger.info(f"Got response: {response}")

    response = google_api_client.send_prompt(prompt="What is the capital of France?", conversation_id="test")
    logger.info(f"Got response: {response}")
    response = google_api_client.send_prompt(prompt="And Germany?", conversation_id="test")
    logger.info(f"Got response: {response}")
    response = google_api_client.send_prompt(prompt="How about Spain?", conversation_id="test")
    logger.info(f"Got response: {response}")
    response = google_api_client.send_prompt(prompt="Describe the image in 1 sentence without describing the thing the cat is lying on.",
                                             image_url="https://agentlegoodbye.com/wp-content/uploads/photo-gallery/thumb/Purrito-4.jpg",
                                             conversation_id="test")
    logger.info(f"Got response: {response}")
    response = google_api_client.send_prompt(prompt="Now tell me the color of the thing the cat is lying on", conversation_id="test")
    logger.info(f"Got response: {response}")