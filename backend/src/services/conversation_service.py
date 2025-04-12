from typing import List, Optional, Dict
from datetime import datetime
import json
import os
from ..models.conversation import Conversation, Message, MessageRole

class ConversationService:
    _instance = None
    _conversations: Dict[str, Conversation] = {}
    _storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "conversations")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationService, cls).__new__(cls)
            cls._instance._load_conversations()
        return cls._instance

    def _load_conversations(self):
        """Charge les conversations depuis le stockage"""
        if not os.path.exists(self._storage_path):
            os.makedirs(self._storage_path)
            return

        for filename in os.listdir(self._storage_path):
            if filename.endswith('.json'):
                with open(os.path.join(self._storage_path, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversation = Conversation(**data)
                    self._conversations[conversation.id] = conversation

    def _save_conversation(self, conversation: Conversation):
        """Sauvegarde une conversation dans le stockage"""
        if not os.path.exists(self._storage_path):
            os.makedirs(self._storage_path)

        filepath = os.path.join(self._storage_path, f"{conversation.id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation.dict(), f, ensure_ascii=False, indent=2)

    def create_conversation(self, title: str, initial_message: Optional[Message] = None) -> Conversation:
        """Crée une nouvelle conversation"""
        conversation = Conversation(title=title)
        if initial_message:
            conversation.add_message(initial_message)
        self._conversations[conversation.id] = conversation
        self._save_conversation(conversation)
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Récupère une conversation par son ID"""
        return self._conversations.get(conversation_id)

    def get_all_conversations(self) -> List[Conversation]:
        """Récupère toutes les conversations"""
        return list(self._conversations.values())

    def add_message(self, conversation_id: str, message: Message) -> Optional[Conversation]:
        """Ajoute un message à une conversation"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.add_message(message)
            self._save_conversation(conversation)
        return conversation

    def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Message]:
        """Récupère les messages d'une conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        return conversation.get_last_messages(limit) if limit else conversation.messages

    def delete_conversation(self, conversation_id: str) -> bool:
        """Supprime une conversation"""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            filepath = os.path.join(self._storage_path, f"{conversation_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        return False

    def update_conversation_title(self, conversation_id: str, new_title: str) -> Optional[Conversation]:
        """Met à jour le titre d'une conversation"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.title = new_title
            conversation.updated_at = datetime.now()
            self._save_conversation(conversation)
        return conversation 