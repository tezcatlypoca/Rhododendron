from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageCreateDTO(BaseModel):
    role: MessageRole = Field(..., description="Rôle de l'émetteur du message")
    content: str = Field(..., description="Contenu du message")
    agent_id: Optional[str] = Field(None, description="ID de l'agent qui a généré le message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Métadonnées du message")

    model_config = ConfigDict(from_attributes=True)

class MessageResponseDTO(BaseModel):
    id: str = Field(..., description="Identifiant unique du message")
    conversation_id: str = Field(..., description="ID de la conversation")
    role: MessageRole = Field(..., description="Rôle de l'émetteur du message")
    content: str = Field(..., description="Contenu du message")
    timestamp: datetime = Field(..., description="Date et heure du message")
    agent_id: Optional[str] = Field(None, description="ID de l'agent qui a généré le message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées du message")

    model_config = ConfigDict(from_attributes=True)

class ConversationCreateDTO(BaseModel):
    title: str = Field(..., description="Titre de la conversation")
    agent_id: Optional[str] = Field(None, description="ID de l'agent associé à la conversation")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Métadonnées de la conversation")

    model_config = ConfigDict(from_attributes=True)

class ConversationUpdateDTO(BaseModel):
    title: Optional[str] = Field(None, description="Titre de la conversation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Métadonnées de la conversation")

    model_config = ConfigDict(from_attributes=True)

class ConversationResponseDTO(BaseModel):
    id: str = Field(..., description="Identifiant unique de la conversation")
    title: str = Field(..., description="Titre de la conversation")
    created_at: datetime = Field(..., description="Date de création de la conversation")
    updated_at: datetime = Field(..., description="Date de dernière modification")
    agent_id: Optional[str] = Field(None, description="ID de l'agent associé à la conversation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées de la conversation")
    messages: List[MessageResponseDTO] = Field(default_factory=list, description="Messages de la conversation")

    model_config = ConfigDict(from_attributes=True) 