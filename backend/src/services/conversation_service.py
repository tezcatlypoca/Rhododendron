from typing import List, Optional, Dict
from datetime import datetime
import json
import os
from ..models.conversation import Conversation, Message, MessageRole

class ConversationService:
    _instance = None
    _conversations: Dict[str, Conversation] = {}
    _data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "conversations")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationService, cls).__new__(cls)
            cls._instance._load_conversations()
        return cls._instance

    def _load_conversations(self):
        """Charge toutes les conversations depuis les fichiers JSON"""
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)
            return

        for filename in os.listdir(self._data_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self._data_dir, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Convertir les chaînes ISO en datetime
                        if "created_at" in data:
                            data["created_at"] = datetime.fromisoformat(data["created_at"])
                        if "updated_at" in data:
                            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                        if "messages" in data:
                            for message in data["messages"]:
                                if "timestamp" in message:
                                    message["timestamp"] = datetime.fromisoformat(message["timestamp"])
                        conversation = Conversation(**data)
                        self._conversations[conversation.id] = conversation
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    print(f"Erreur lors du chargement de {filename}: {str(e)}")
                    # Si le fichier est corrompu, on le supprime
                    os.remove(os.path.join(self._data_dir, filename))

    def _save_conversation(self, conversation: Conversation):
        """Sauvegarde une conversation dans un fichier JSON"""
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)

        file_path = os.path.join(self._data_dir, f"{conversation.id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            # Utiliser model_dump_json pour la sérialisation
            f.write(conversation.model_dump_json(indent=2))

    def create_conversation(self, title: str) -> Conversation:
        """Crée une nouvelle conversation"""
        conversation = Conversation(title=title)
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
        if conversation:
            return conversation.get_last_messages(limit)
        return []

    def delete_conversation(self, conversation_id: str) -> bool:
        """Supprime une conversation"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            file_path = os.path.join(self._data_dir, f"{conversation_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            del self._conversations[conversation_id]
            return True
        return False

    def update_conversation_title(self, conversation_id: str, new_title: str) -> Optional[Conversation]:
        """Met à jour le titre d'une conversation"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.title = new_title
            self._save_conversation(conversation)
        return conversation 