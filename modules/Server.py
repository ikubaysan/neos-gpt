from flask import Flask, request, jsonify
import time
from modules.APIClient import APIClient
from modules.Config import Config
from modules.helpers.logging_helper import logger

class Server:
    def __init__(self, api_client: APIClient, config: Config):
        self.config = config
        self.api_client = api_client
        self.min_seconds_between_requests_per_user = config.min_seconds_between_requests_per_user
        self.callers = {}

        # Using Flask synchronously
        self.app = Flask(__name__)
        self.app.route("/prompt", methods=["POST"])(self.handle_prompt)

    def handle_prompt(self):
        # Neos does not support parsing JSON,
        # so we return a string with exactly the text we want to display
        caller = request.remote_addr
        current_time = time.time()

        if caller in self.callers:
            time_diff = current_time - self.callers[caller]
            if time_diff < self.min_seconds_between_requests_per_user:
                return jsonify({"error": "Too many requests"}), 429

        self.callers[caller] = current_time

        text = request.data.decode("utf-8")
        if len(text) > self.config.max_prompt_chars:
            text = text[:self.config.max_prompt_chars]

        logger.info(f"Received prompt: {text}")

        try:
            response = self.api_client.send_prompt(prompt=text)
            logger.info(f"Got response: {response}")
        except Exception as e:
            logger.error(f"Error: {e}")
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

