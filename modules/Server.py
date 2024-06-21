from flask import Flask, request, jsonify
import time
import re
from modules.OpenAIAPIClient import OpenAIAPIClient
from modules.GoogleAIAPIClient import GoogleAIAPIClient
from modules.Config import Config
from modules.helpers.logging_helper import logger
import traceback
from typing import List, Optional

class Server:
    def __init__(self, openai_api_client: OpenAIAPIClient, google_ai_api_client: GoogleAIAPIClient, config: Config):
        self.config = config
        self.openai_api_client = openai_api_client
        self.google_ai_api_client = google_ai_api_client
        self.min_seconds_between_requests_per_user = config.min_seconds_between_requests_per_user
        self.callers = {}
        self.valid_models = config.openai_models + [config.google_model]
        logger.info(f"Valid models: {self.valid_models} ({len(self.valid_models)} total)")

        # Using Flask synchronously
        self.app = Flask(__name__)
        self.app.route("/prompt", methods=["POST"])(self.handle_prompt)

    def is_valid_guid(self, guid):
        # Check length
        if len(guid) > 36:
            return False
        # Check for invalid characters
        if not re.match("^[a-zA-Z0-9-]+$", guid):
            return False
        return True

    def handle_prompt(self):
        caller = request.remote_addr
        current_time = time.time()

        if caller not in self.config.whitelist and self.config.whitelist_enabled:
            return jsonify({"error": "Your IP is not whitelisted"}), 403

        if caller in self.callers:
            time_diff = current_time - self.callers[caller]
            if time_diff < self.min_seconds_between_requests_per_user:
                return jsonify({"error": "Too many requests"}), 429

        conversation_id = request.args.get("conversation_id")
        if conversation_id is not None and not self.is_valid_guid(conversation_id):
            return jsonify({"error": "Invalid conversation_id"}), 400

        models_str = request.args.get("models")
        models = [item.strip() for item in models_str.split(',')]

        for model in models:
            if model not in self.valid_models:
                return jsonify({"error": f"Invalid model: {models}"}), 400

        if self.min_seconds_between_requests_per_user > 0:
            self.callers[caller] = current_time

        text = request.data.decode("utf-8")
        if len(text) > self.config.openai_max_prompt_chars:
            text = text[:self.config.openai_max_prompt_chars]

        logger.info(f"Received prompt: {text}")
        image_url = request.args.get("image_url")

        if image_url:
            if "{" in image_url or "}" in image_url:
                return f"Invalid image_url: {image_url}", 400
            logger.info(f"An image_url was included: {image_url}")
            # Replace all "|" with "/" in the image URL
            image_url = image_url.replace("|", "/")
            logger.info(f"Image URL after replacing | with /: {image_url}")

        response = self.send_prompt(models=models,
                         text=text,
                         image_url=image_url,
                         conversation_id=conversation_id)

        self.delete_old_callers()

        return response, 200


    def send_prompt(self, models: List[str], text: str, image_url: str, conversation_id: Optional[str]) -> str:
        logger.info(f"Sending prompt to {len(models)} models: {models}")
        responses = {}
        for model in models:
            try:
                if model == self.config.google_model:
                    response = self.google_ai_api_client.send_prompt(prompt=text,
                                                                      image_url=image_url,
                                                                      conversation_id=conversation_id)
                else:
                    response = self.openai_api_client.send_prompt(prompt=text,
                                                           image_url=image_url,
                                                           conversation_id=conversation_id,
                                                           model=model)
                responses[model] = response
                logger.info(f"Got response from model {model}: {response}")
            except Exception as e:
                traceback_str = traceback.format_exc()
                logger.error(f"Failed to send prompt to model '{model}': {traceback_str}")
                responses[model] = f"Failed to send prompt to model '{model}': {e}"

        if len(models) == 1:
            return responses[models[0]]

        combined_response = ""

        for i in range(len(models)):
            model = models[i]
            if i == len(models) - 1:
                #combined_response += f"Model: {model}\n{responses[model]}"
                combined_response += f"Response from model '{model}':\n{responses[model]}"
            else:
                #combined_response += f"Model: {model}\n{responses[model]}\n\n"
                combined_response += f"Response from model '{model}':\n{responses[model]}\n\n\n"

        return combined_response

    def delete_old_callers(self):
        current_time = time.time()
        for caller in self.callers.copy():
            time_diff = current_time - self.callers[caller]
            if time_diff > self.min_seconds_between_requests_per_user:
                del self.callers[caller]

    def run(self):
        self.app.run(host=self.config.host, port=self.config.port)
        logger.info(f"Server started on {self.config.host}:{self.config.port}")
