

class Dialogue:
    def __init__(self, prompt_message: dict, response_message: dict, model: str):
        self.prompt_message = prompt_message
        self.prompt_text = prompt_message["content"][0]["text"].strip()
        self.response_message = response_message
        self.response_text = response_message["content"].strip()
        self.prompt_num_tokens = get_num_tokens_from_string(self.prompt_text, model)
        self.response_num_tokens = get_num_tokens_from_string(self.response_text, model)
        self.total_num_tokens = self.prompt_num_tokens + self.response_num_tokens
