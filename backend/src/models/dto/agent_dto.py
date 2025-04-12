from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AgentCreateDTO(BaseModel):
    name: str = Field(..., description="Nom de l'agent")
    model_type: str = Field(..., description="Type de modèle utilisé par l'agent")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuration de l'agent")

class AgentUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, description="Nom de l'agent")
    model_type: Optional[str] = Field(None, description="Type de modèle utilisé par l'agent")
    is_active: Optional[bool] = Field(None, description="Statut d'activation de l'agent")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration de l'agent")

class AgentResponseDTO(BaseModel):
    id: str = Field(..., description="Identifiant unique de l'agent")
    name: str = Field(..., description="Nom de l'agent")
    model_type: str = Field(..., description="Type de modèle utilisé par l'agent")
    is_active: bool = Field(..., description="Statut d'activation de l'agent")
    created_at: datetime = Field(..., description="Date de création de l'agent")
    last_used: Optional[datetime] = Field(None, description="Dernière utilisation de l'agent")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration de l'agent")

class AgentRequestDTO(BaseModel):
    prompt: str = Field(..., description="Prompt à envoyer à l'agent")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Paramètres supplémentaires pour la requête")

class AgentResponseRequestDTO(BaseModel):
    status: str = Field(..., description="Statut de la requête")
    response: str = Field(..., description="Réponse de l'agent")
    timestamp: datetime = Field(..., description="Horodatage de la réponse") 