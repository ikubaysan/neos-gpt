from modules.Config import Config
from modules.APIClient import APIClient
from modules.Server import Server
from modules.helpers.logging_helper import logger

if __name__ == '__main__':
    config = Config('config.ini')
    api_client = APIClient(base_url=config.base_url, path=config.path, api_key=config.api_key, model=config.model, 
                           max_conversation_tokens=config.max_conversation_tokens,
                           max_response_tokens=config.max_response_tokens,
                           max_dialogues_per_conversation=config.max_dialogues_per_conversation,
                           conversation_prune_after_seconds=config.conversation_prune_after_seconds,
                           temperature=config.temperature, system_message=config.system_message)
    server = Server(api_client=api_client, config=config)
    server.run()
