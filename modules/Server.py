from flask import Flask, request, jsonify
import time
import re
from modules.APIClient import APIClient
from modules.Config import Config
from modules.helpers.logging_helper import logger
import traceback

class Server:
    def __init__(self, api_client: APIClient, config: Config):
        self.config = config
        self.api_client = api_client
        self.min_seconds_between_requests_per_user = config.min_seconds_between_requests_per_user
        self.callers = {}

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

        model = request.args.get("model")
        # TODO: validate this better
        if model is not None and len(model) < 1:
            return jsonify({"error": "Invalid model"}), 400

        if self.min_seconds_between_requests_per_user > 0:
            self.callers[caller] = current_time

        text = request.data.decode("utf-8")
        if len(text) > self.config.max_prompt_chars:
            text = text[:self.config.max_prompt_chars]

        logger.info(f"Received prompt: {text}")
        image_url = request.args.get("image_url")

        if image_url:
            logger.info(f"An image_url was included: {image_url}")
            # Replace all "|" with "/" in the image URL
            image_url = image_url.replace("|", "/")
            logger.info(f"Image URL after replacing | with /: {image_url}")

        try:
            # Pass the conversation_id to the API client
            response = self.api_client.send_prompt(prompt=text,
                                                   image_url=image_url,
                                                   conversation_id=conversation_id,
                                                   model=model)
            logger.info(f"Got response: {response}")
        except Exception as e:
            # log the traceback
            logger.error(traceback.format_exc())
            return f"Could not process request to OpenAI API: {e}", 500

        self.delete_old_callers()

        return response, 200

    def delete_old_callers(self):
        current_time = time.time()
        for caller in self.callers.copy():
            time_diff = current_time - self.callers[caller]
            if time_diff > self.min_seconds_between_requests_per_user:
                del self.callers[caller]

    def run(self):
        self.app.run(host=self.config.host, port=self.config.port)
        logger.info(f"Server started on {self.config.host}:{self.config.port}")
