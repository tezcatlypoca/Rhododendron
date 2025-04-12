from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class AgentCreateDTO(BaseModel):
    name: str = Field(..., description="Nom de l'agent")
    model_type: str = Field(..., description="Type de modèle utilisé par l'agent")  
    role: str = Field(default="assistant", description="Rôle de l'agent")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuration de l'agent")

    model_config = ConfigDict(from_attributes=True)

class AgentUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, description="Nom de l'agent")
    model_type: Optional[str] = Field(None, description="Type de modèle utilisé par l'agent")
    role: Optional[str] = Field(None, description="Rôle de l'agent")
    is_active: Optional[bool] = Field(None, description="Statut d'activation de l'agent")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration de l'agent")

    model_config = ConfigDict(from_attributes=True)

class AgentResponseDTO(BaseModel):
    id: str = Field(..., description="Identifiant unique de l'agent")
    name: str = Field(..., description="Nom de l'agent")
    model_type: str = Field(..., description="Type de modèle utilisé par l'agent")
    role: str = Field(..., description="Rôle de l'agent")
    is_active: bool = Field(..., description="Statut d'activation de l'agent")
    created_at: datetime = Field(..., description="Date de création de l'agent")
    last_used: Optional[datetime] = Field(None, description="Dernière utilisation de l'agent")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration de l'agent")

    model_config = ConfigDict(from_attributes=True)

class AgentRequestDTO(BaseModel):
    prompt: str = Field(..., description="Prompt à envoyer à l'agent")
    conversation_id: Optional[str] = Field(None, description="ID de la conversation associée")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Paramètres supplémentaires pour la requête")

    model_config = ConfigDict(from_attributes=True)

class AgentResponseRequestDTO(BaseModel):
    status: str = Field(..., description="Statut de la requête")
    response: str = Field(..., description="Réponse de l'agent")
    timestamp: datetime = Field(..., description="Horodatage de la réponse")
    conversation_id: Optional[str] = Field(None, description="ID de la conversation associée")
    agent_id: Optional[str] = Field(None, description="ID de l'agent qui a généré la réponse")

    model_config = ConfigDict(from_attributes=True) 