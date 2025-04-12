from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ...database import get_db
from ...models.dto.agent_dto import (
    AgentCreateDTO,
    AgentUpdateDTO,
    AgentResponseDTO,
    AgentRequestDTO,
    AgentResponseRequestDTO
)
from ...services.agent_service import AgentService

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={
        404: {"description": "Agent non trouvé"},
        400: {"description": "Requête invalide"}
    }
)

# Création d'une instance du service
agent_service = AgentService()

class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    role: str = "assistant"
    config: Optional[Dict[str, Any]] = None

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class AgentRequest(BaseModel):
    message: str
    metadata: Optional[Dict[str, Any]] = None

@router.post(
    "/",
    response_model=AgentResponseDTO,
    summary="Créer un nouvel agent",
    description="Crée un nouvel agent avec les paramètres spécifiés."
)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Crée un nouvel agent"""
    return agent_service.create_agent(agent_data, db)

@router.get(
    "/",
    response_model=List[AgentResponseDTO],
    summary="Lister tous les agents",
    description="Récupère la liste complète de tous les agents disponibles dans le système."
)
async def list_agents(db: Session = Depends(get_db)):
    """Liste tous les agents"""
    return agent_service.get_all_agents(db)

@router.get(
    "/{agent_id}",
    response_model=AgentResponseDTO,
    summary="Récupérer un agent",
    description="Récupère les détails d'un agent spécifique par son identifiant unique."
)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Récupère un agent par son ID"""
    agent = agent_service.get_agent(agent_id, db)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return agent

@router.put(
    "/{agent_id}",
    response_model=AgentResponseDTO,
    summary="Mettre à jour un agent",
    description="Met à jour les propriétés d'un agent existant."
)
async def update_agent(agent_id: str, agent_data: AgentUpdate, db: Session = Depends(get_db)):
    """Met à jour un agent"""
    agent = agent_service.update_agent(agent_id, agent_data, db)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return agent

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Supprime un agent"""
    success = agent_service.delete_agent(agent_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return {"message": "Agent supprimé avec succès"}

@router.post(
    "/{agent_id}/request",
    response_model=AgentResponseRequestDTO,
    summary="Traiter une requête",
    description="Envoie une requête à un agent spécifique pour traitement."
)
async def process_request(agent_id: str, request_data: AgentRequest, db: Session = Depends(get_db)):
    """Traite une requête avec un agent"""
    response = agent_service.process_request(agent_id, request_data, db)
    if not response:
        raise HTTPException(status_code=404, detail="Agent non trouvé ou inactif")
    return response 