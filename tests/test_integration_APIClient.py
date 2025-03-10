from modules.Config import Config
from modules.OpenAIAPIClient import APIClient, ConversationContainer, Conversation, Dialogue, get_num_tokens_from_string
import os
import pytest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def api_client():
    config = Config(os.path.join(base_dir, 'config.ini'))
    return APIClient(base_url=config.base_url,
                     path=config.path,
                     api_key=config.api_key,
                     model=config.model,
                     max_conversation_tokens=config.max_conversation_tokens,
                     max_response_tokens=config.max_response_tokens,
                     temperature=config.temperature,
                     conversation_prune_after_seconds=config.conversation_prune_after_seconds,
                     max_dialogues_per_conversation=config.max_dialogues_per_conversation
                     )

def test_APIClient_send_prompt_english(api_client: APIClient):
    response = api_client.send_prompt(prompt="What is 9 plus 10?")
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

def test_APIClient_send_prompt_japanese(api_client: APIClient):
    response = api_client.send_prompt(prompt="9たす10は何ですか？")
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

