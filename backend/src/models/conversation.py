from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from uuid import uuid4

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: Optional[str] = None  # ID de l'agent qui a généré la réponse
    metadata: Optional[dict] = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    participants: List[str] = Field(default_factory=list)  # Liste des IDs des participants
    agent_id: Optional[str] = None  # ID de l'agent associé à la conversation
    metadata: Optional[dict] = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    def add_message(self, message: Message) -> None:
        """Ajoute un message à la conversation et met à jour la date de modification"""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_last_messages(self, limit: Optional[int] = None) -> List[Message]:
        """Récupère les derniers messages de la conversation"""
        if limit is None:
            return self.messages
        return self.messages[-limit:]

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