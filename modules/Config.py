import configparser
import os


class Config:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        if not os.path.exists(self.config_file_path):
            raise Exception(f"Config file not found at {self.config_file_path}")
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)

        # TODO: encryption instead of reading plaintext
        self.openai_base_url = self.config['openai_api_client']['base_url']
        self.openai_path = self.config['openai_api_client']['path']
        self.openai_api_key = self.config['openai_api_client']['api_key']
        self.openai_model = self.config['openai_api_client']['model']
        self.openai_max_conversation_tokens = int(self.config['openai_api_client']['max_conversation_tokens'])
        self.openai_max_response_tokens = int(self.config['openai_api_client']['max_response_tokens'])
        self.openai_max_dialogues_per_conversation = int(self.config['openai_api_client']['max_dialogues_per_conversation'])
        self.openai_conversation_prune_after_seconds = int(self.config['openai_api_client']['conversation_prune_after_seconds'])
        self.openai_temperature = float(self.config['openai_api_client']['temperature'])
        self.openai_max_prompt_chars = int(self.config['openai_api_client']['max_prompt_chars'])
        self.openai_system_message = self.config['openai_api_client']['system_message'] if len(self.config['openai_api_client']['system_message']) > 0 else None

        self.google_api_key = self.config['google_api_client']['api_key']
        self.google_model = self.config['google_api_client']['model']

        self.whitelist_enabled = self.config['server']['whitelist_enabled'].lower() == 'true'
        self.whitelist = [item.strip() for item in self.config['server']['whitelist'].split(',') if self.whitelist_enabled]

        self.min_seconds_between_requests_per_user = float(self.config['server']['min_seconds_between_requests_per_user'])
        self.min_seconds_between_requests_per_user = self.min_seconds_between_requests_per_user if self.min_seconds_between_requests_per_user > 0 else 0

        self.host = self.config['server']['host']
        self.port = int(self.config['server']['port'])
