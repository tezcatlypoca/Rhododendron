from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.models.dto.agent_dto import (
    AgentCreateDTO,
    AgentUpdateDTO,
    AgentResponseDTO,
    AgentRequestDTO,
    AgentResponseRequestDTO
)
from src.services.agent_service import AgentService

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

@router.post(
    "/",
    response_model=AgentResponseDTO,
    summary="Créer un nouvel agent",
    description="Crée un nouvel agent avec les paramètres spécifiés. L'agent sera initialisé avec les configurations fournies."
)
async def create_agent(agent_dto: AgentCreateDTO):
    """Crée un nouvel agent"""
    return agent_service.create_agent(agent_dto)

@router.get(
    "/",
    response_model=List[AgentResponseDTO],
    summary="Lister tous les agents",
    description="Récupère la liste complète de tous les agents disponibles dans le système."
)
async def list_agents():
    """Récupère la liste de tous les agents"""
    return agent_service.list_agents()

@router.get(
    "/{agent_id}",
    response_model=AgentResponseDTO,
    summary="Récupérer un agent",
    description="Récupère les détails d'un agent spécifique par son identifiant unique."
)
async def get_agent(agent_id: str):
    """Récupère un agent par son ID"""
    agent = agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return agent

@router.put(
    "/{agent_id}",
    response_model=AgentResponseDTO,
    summary="Mettre à jour un agent",
    description="Met à jour les propriétés d'un agent existant. Seuls les champs fournis seront modifiés."
)
async def update_agent(agent_id: str, agent_dto: AgentUpdateDTO):
    """Met à jour un agent"""
    agent = agent_service.update_agent(agent_id, agent_dto)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return agent

@router.post(
    "/{agent_id}/request",
    response_model=AgentResponseRequestDTO,
    summary="Traiter une requête",
    description="Envoie une requête à un agent spécifique pour traitement. L'agent doit être actif pour traiter la requête."
)
async def process_request(agent_id: str, request_dto: AgentRequestDTO):
    """Traite une requête avec un agent"""
    response = agent_service.process_request(agent_id, request_dto)
    if not response:
        raise HTTPException(status_code=404, detail="Agent non trouvé ou inactif")
    return response 