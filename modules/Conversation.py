


class Conversation:
    def __init__(self, max_length: int, model: str):
        self.max_length = max_length
        self.update_epoch = time.time()
        self.dialogues: List[Dialogue] = []
        self.model = model

    def add(self, prompt_message: dict, response_message: dict):
        dialogue = Dialogue(prompt_message, response_message, self.model)
        if len(self.dialogues) == self.max_length:
            self.dialogues.pop(0)
        self.dialogues.append(dialogue)
        self.update_epoch = time.time()

    def get_messages_for_api(self):
        messages = []
        for dialogue in self.dialogues:
            messages.append(dialogue.prompt_message)
            messages.append(dialogue.response_message)
        return messages

    def get_total_tokens(self):
        return sum([dialogue.total_num_tokens for dialogue in self.dialogues])

    def trim(self, prompt_tokens: int, token_limit: int):
        # Remove dialogues until the total number of the prompt and saved dialogues is less than the token limit
        while len(self.dialogues) > 0 and self.get_total_tokens() + prompt_tokens >= token_limit:
            self.dialogues.pop(0)