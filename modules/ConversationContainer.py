from modules.Conversation import Conversation, OpenAIConversation, GoogleAIConversation
from abc import ABC, abstractmethod


class ConversationContainer(ABC):
    @abstractmethod
    def get_conversation(self, conversation_id: str, model: str) -> Conversation:
        pass


class OpenAIConversationContainer(ConversationContainer):
    def __init__(self, conversation_prune_after_seconds: int, max_dialogues_per_conversation: int):
        self.conversation_prune_after_seconds = conversation_prune_after_seconds
        self.max_dialogues_per_conversation = max_dialogues_per_conversation
        self.conversations = {}

    def get_conversation(self, conversation_id: str, model: str) -> OpenAIConversation:
        if conversation_id not in self.conversations:
            # Create a new conversation if it doesn't exist
            self.conversations[conversation_id] = OpenAIConversation(max_length=self.max_dialogues_per_conversation,
                                                                     model=model)
        return self.conversations[conversation_id]


class GoogleConversationContainer(ConversationContainer):
    def __init__(self, conversation_prune_after_seconds: int, max_dialogues_per_conversation: int, model: str):
        self.conversation_prune_after_seconds = conversation_prune_after_seconds
        self.max_dialogues_per_conversation = max_dialogues_per_conversation
        self.conversations = {}
        self.model = model

    def get_conversation(self, conversation_id: str, model: str) -> GoogleAIConversation:
        if conversation_id not in self.conversations:
            # Create a new conversation if it doesn't exist
            self.conversations[conversation_id] = GoogleAIConversation(max_length=self.max_dialogues_per_conversation,
                                                                       model=model)
        return self.conversations[conversation_id]
