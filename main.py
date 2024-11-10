from modules.Config import Config
from modules.OpenAIAPIClient import OpenAIAPIClient
from modules.GoogleAIAPIClient import GoogleAIAPIClient
from modules.ClaudeAPIClient import ClaudeAPIClient
from modules.Server import Server
from modules.helpers.logging_helper import logger

if __name__ == '__main__':
    config = Config('config.ini')
    openai_api_client = OpenAIAPIClient(base_url=config.openai_base_url, path=config.openai_path,
                                        api_key=config.openai_api_key,
                           max_conversation_tokens=config.openai_max_conversation_tokens,
                           max_response_tokens=config.openai_max_response_tokens,
                           max_dialogues_per_conversation=config.openai_max_dialogues_per_conversation,
                           conversation_prune_after_seconds=config.openai_conversation_prune_after_seconds,
                           temperature=config.openai_temperature, system_message=config.openai_system_message)

    google_api_client = GoogleAIAPIClient(api_key=config.google_api_key,
                                          model_name=config.google_model,
                                          conversation_prune_after_seconds=config.openai_conversation_prune_after_seconds,
                                          max_dialogues_per_conversation=config.openai_max_dialogues_per_conversation)

    claude_api_client = ClaudeAPIClient(api_key=config.claude_api_key,
                                        model_name=config.claude_model,
                                        conversation_prune_after_seconds=config.openai_conversation_prune_after_seconds,
                                        max_dialogues_per_conversation=config.openai_max_dialogues_per_conversation)

    server = Server(openai_api_client=openai_api_client,
                    google_ai_api_client=google_api_client,
                    claude_api_client=claude_api_client,
                    config=config)
    server.run()
