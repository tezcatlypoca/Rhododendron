from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message:
    def __init__(
        self,
        role: MessageRole,
        content: str,
        id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        self.id = id or str(uuid4())
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.agent_id = agent_id
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        """Convertit le message en dictionnaire"""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Crée une instance de Message à partir d'un dictionnaire"""
        return cls(
            id=data.get("id"),
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            agent_id=data.get("agent_id"),
            metadata=data.get("metadata", {})
        )

class Conversation:
    def __init__(
        self,
        title: str,
        id: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        self.id = id or str(uuid4())
        self.title = title
        self.messages = messages or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.agent_id = agent_id
        self.metadata = metadata or {}

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

    def to_dict(self) -> dict:
        """Convertit la conversation en dictionnaire"""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "agent_id": self.agent_id,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Conversation':
        """Crée une instance de Conversation à partir d'un dictionnaire"""
        return cls(
            id=data.get("id"),
            title=data["title"],
            messages=[Message.from_dict(msg) for msg in data.get("messages", [])],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            agent_id=data.get("agent_id"),
            metadata=data.get("metadata", {})
        ) 