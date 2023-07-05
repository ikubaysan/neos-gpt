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
        self.api_key = self.config['api_client']['api_key']
        self.base_url = self.config['api_client']['base_url']
        self.path = self.config['api_client']['path']
        self.model = self.config['api_client']['model']
        self.max_response_tokens = int(self.config['api_client']['max_response_tokens'])
        self.temperature = float(self.config['api_client']['temperature'])
        self.max_prompt_chars = int(self.config['api_client']['max_prompt_chars'])
        self.prompt_history_length = int(self.config['api_client']['prompt_history_length'])
        self.system_message = self.config['api_client']['system_message']

        self.whitelist_enabled = self.config['server']['whitelist_enabled'].lower() == 'true'
        self.whitelist = [item.strip() for item in self.config['server']['whitelist'].split(',') if self.whitelist_enabled]

        self.min_seconds_between_requests_per_user = float(self.config['server']['min_seconds_between_requests_per_user'])
        self.min_seconds_between_requests_per_user = self.min_seconds_between_requests_per_user if self.min_seconds_between_requests_per_user > 0 else 0

        self.host = self.config['server']['host']
        self.port = int(self.config['server']['port'])
