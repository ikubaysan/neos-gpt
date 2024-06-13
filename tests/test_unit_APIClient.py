from modules.OpenAIAPIClient import APIClient, ConversationContainer, Conversation, Dialogue, get_num_tokens_from_string
import os
import pytest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Hardcoded test data
PROMPT = "What is 9 plus 10?"
RESPONSE = "The answer is 19."
MODEL = "gpt-3.5-turbo"
TOKEN_LIMIT = 20  # Arbitrary limit

@pytest.fixture
def dialogue():
    return Dialogue(PROMPT, RESPONSE, MODEL)


@pytest.fixture
def conversation():
    return Conversation(max_length=5, model=MODEL)


def test_get_num_tokens_from_string_english():
    num_tokens = get_num_tokens_from_string(string="What is 9 plus 10?", encoding_name="gpt-3.5-turbo")
    assert num_tokens == 8


def test_dialogue_init(dialogue):
    assert dialogue.prompt == PROMPT
    assert dialogue.response == RESPONSE
    assert dialogue.prompt_num_tokens == get_num_tokens_from_string(PROMPT, MODEL)
    assert dialogue.response_num_tokens == get_num_tokens_from_string(RESPONSE, MODEL)
    assert dialogue.total_num_tokens == dialogue.prompt_num_tokens + dialogue.response_num_tokens


def test_conversation_init(conversation):
    assert conversation.max_length == 5
    assert len(conversation.dialogues) == 0


def test_conversation_add(conversation, dialogue):
    conversation.add(dialogue.prompt, dialogue.response)
    assert len(conversation.dialogues) == 1
    assert conversation.dialogues[0].prompt == dialogue.prompt
    assert conversation.dialogues[0].response == dialogue.response


def test_conversation_get_messages_for_api(conversation, dialogue):
    conversation.add(dialogue.prompt, dialogue.response)
    messages = conversation.get_messages_for_api()
    assert len(messages) == 2
    assert messages[0]['role'] == 'user'
    assert messages[0]['content'] == dialogue.prompt
    assert messages[1]['role'] == 'assistant'
    assert messages[1]['content'] == dialogue.response


def test_conversation_get_total_tokens(conversation, dialogue):
    conversation.add(dialogue.prompt, dialogue.response)
    total_tokens = conversation.get_total_tokens()
    assert total_tokens == dialogue.total_num_tokens


def test_conversation_trim(conversation, dialogue):
    for _ in range(6):  # Add more dialogues than max_length
        conversation.add(dialogue.prompt, dialogue.response)
    assert len(conversation.dialogues) == conversation.max_length  # Check trimming from adding
    prompt_tokens = get_num_tokens_from_string(PROMPT, MODEL)
    conversation.trim(prompt_tokens=prompt_tokens, token_limit=TOKEN_LIMIT)
    assert len(conversation.dialogues) < conversation.max_length  # Check trimming by token limit
