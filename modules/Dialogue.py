from modules.helpers.prompt_helpers import get_num_tokens_from_string

# class Dialogue:
#     def __init__(self, prompt_message: dict, response_message: dict, model: str):
#         self.prompt_message = prompt_message
#         self.prompt_text = prompt_message["content"][0]["text"].strip()
#         self.response_message = response_message
#         self.response_text = response_message["content"].strip()
#         self.prompt_num_tokens = get_num_tokens_from_string(self.prompt_text, model)
#         self.response_num_tokens = get_num_tokens_from_string(self.response_text, model)
#         self.total_num_tokens = self.prompt_num_tokens + self.response_num_tokens



class OpenAIDialogue:
    def __init__(self, prompt_message: dict, response_message: dict, model: str):
        self.prompt_message = prompt_message
        self.prompt_text = prompt_message["content"][0]["text"].strip()
        self.response_message = response_message
        self.response_text = response_message["content"].strip()
        self.prompt_num_tokens = get_num_tokens_from_string(self.prompt_text, model)
        self.response_num_tokens = get_num_tokens_from_string(self.response_text, model)
        self.total_num_tokens = self.prompt_num_tokens + self.response_num_tokens


class GoogleAIDialogue:
    def __init__(self, prompt_contents: dict, response_text: str):
        self.prompt_contents = prompt_contents
        self.response_text = response_text
