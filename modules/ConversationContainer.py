from modules.Conversation import Conversation

class ConversationContainer:
    def __init__(self, conversation_prune_after_seconds: int, max_dialogues_per_conversation: int, model: str):
        self.conversation_prune_after_seconds = conversation_prune_after_seconds
        self.max_dialogues_per_conversation = max_dialogues_per_conversation
        self.conversations = {}
        self.model = model

    def get_conversation(self, conversation_id: str) -> Conversation:
        if conversation_id not in self.conversations:
            # Create a new conversation if it doesn't exist
            self.conversations[conversation_id] = Conversation(max_length=self.max_dialogues_per_conversation, model=self.model)
        return self.conversations[conversation_id]