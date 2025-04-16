from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import time

from ...database import get_db
from ...models.dto.agent_dto import (
    AgentCreateDTO,
    AgentUpdateDTO,
    AgentResponseDTO,
    AgentRequestDTO,
    AgentResponseRequestDTO
)
from ...services.agent_service import AgentService
from ...services.llm_interface import LLMInterface
from ...models.domain.conversation import MessageRole
from pydantic import BaseModel

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

class AgentRequest(BaseModel):
    """Modèle pour les requêtes d'agent"""
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000

class AgentResponse(BaseModel):
    """Modèle pour les réponses d'agent"""
    response: str
    processing_time: float

@router.post(
    "/",
    response_model=AgentResponseDTO,
    summary="Créer un nouvel agent",
    description="Crée un nouvel agent avec les paramètres spécifiés."
)
async def create_agent(agent_data: AgentCreateDTO, db: Session = Depends(get_db)):
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
async def update_agent(agent_id: str, agent_data: AgentUpdateDTO, db: Session = Depends(get_db)):
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

@router.post("/{agent_id}/request", response_model=AgentResponse)
async def process_agent_request(
    agent_id: str,
    request: AgentRequest
) -> Dict[str, Any]:
    """
    Traite une requête pour un agent spécifique.
    
    Args:
        agent_id: Identifiant de l'agent
        request: Requête contenant le prompt et les paramètres d'inférence
        
    Returns:
        Réponse de l'agent avec le temps de traitement
    """
    try:
        # Initialiser l'interface LLM
        llm = LLMInterface()
        
        # Charger le modèle si ce n'est pas déjà fait
        if llm._model is None:
            llm.load_model()
        
        # Préparer le contexte
        context = {
            "role": "assistant",
            "agent_id": agent_id
        }
        
        # Générer la réponse
        start_time = time.time()
        response = llm.generate_response(
            prompt=request.prompt,
            context=context,
            conversation_history=None,  # Pas d'historique pour l'instant
            params={
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "top_p": 0.9,
                "stop": ["Utilisateur:", "\n\n"]
            }
        )
        processing_time = time.time() - start_time
        
        return {
            "response": response,
            "processing_time": processing_time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de la requête : {str(e)}"
        )