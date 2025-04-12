from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import uuid

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: Optional[str] = None  # ID de l'agent qui a généré la réponse
    metadata: Optional[dict] = None

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[Message] = []
    participants: List[str] = []  # Liste des IDs des participants
    agent_id: Optional[str] = None  # ID de l'agent associé à la conversation
    metadata: Optional[dict] = None

    def add_message(self, message: Message) -> None:
        """Ajoute un message à la conversation et met à jour la date de modification"""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_last_messages(self, n: int = 10) -> List[Message]:
        """Récupère les n derniers messages de la conversation"""
        return self.messages[-n:]

    def get_messages_by_role(self, role: MessageRole) -> List[Message]:
        """Récupère tous les messages d'un rôle spécifique"""
        return [msg for msg in self.messages if msg.role == role]

    def add_participant(self, participant_id: str) -> None:
        """Ajoute un participant à la conversation"""
        if participant_id not in self.participants:
            self.participants.append(participant_id)

    def remove_participant(self, participant_id: str) -> None:
        """Retire un participant de la conversation"""
        if participant_id in self.participants:
            self.participants.remove(participant_id) 