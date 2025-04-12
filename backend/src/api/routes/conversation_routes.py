from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ...models.domain.conversation import Message, MessageRole
from ...database.models import Conversation
from ...models.dto.conversation_dto import (
    ConversationCreateDTO,
    ConversationUpdateDTO,
    ConversationResponseDTO,
    MessageCreateDTO,
    MessageResponseDTO
)
from ...services.conversation_service import ConversationService
from ...services.agent_service import AgentService
from ...database import get_db
from datetime import datetime

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={
        404: {"description": "Conversation non trouvée"},
        400: {"description": "Requête invalide"}
    }
)

conversation_service = ConversationService()
agent_service = AgentService()

class ConversationCreate(BaseModel):
    title: str
    agent_id: Optional[str] = None

class UpdateAgentDTO(BaseModel):
    agent_id: Optional[str] = None

class UpdateTitleDTO(BaseModel):
    title: str

class MessageCreate(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MessageLimit(BaseModel):
    limit: Optional[int] = None

@router.post(
    "/",
    response_model=ConversationResponseDTO,
    summary="Créer une nouvelle conversation",
    description="Crée une nouvelle conversation avec les paramètres spécifiés."
)
async def create_conversation(conversation_data: ConversationCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle conversation"""
    return conversation_service.create_conversation(conversation_data, db)

@router.get(
    "/",
    response_model=List[ConversationResponseDTO],
    summary="Lister toutes les conversations",
    description="Récupère la liste complète de toutes les conversations."
)
async def list_conversations(db: Session = Depends(get_db)):
    """Liste toutes les conversations"""
    return conversation_service.get_all_conversations(db)

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponseDTO,
    summary="Récupérer une conversation",
    description="Récupère les détails d'une conversation spécifique par son identifiant unique."
)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Récupère une conversation par son ID"""
    conversation = conversation_service.get_conversation(conversation_id, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation

@router.put(
    "/{conversation_id}",
    response_model=ConversationResponseDTO,
    summary="Mettre à jour une conversation",
    description="Met à jour les propriétés d'une conversation existante."
)
async def update_conversation(
    conversation_id: str,
    conversation_data: ConversationUpdateDTO,
    db: Session = Depends(get_db)
):
    """Met à jour une conversation"""
    conversation = conversation_service.update_conversation(conversation_id, conversation_data, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Supprime une conversation"""
    success = conversation_service.delete_conversation(conversation_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return {"message": "Conversation supprimée avec succès"}

@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponseDTO,
    summary="Ajouter un message",
    description="Ajoute un nouveau message à une conversation existante."
)
async def add_message(conversation_id: str, message_data: MessageCreate, db: Session = Depends(get_db)):
    """Ajoute un message à une conversation"""
    message = conversation_service.add_message(conversation_id, message_data, db)
    if not message:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return message

@router.get(
    "/{conversation_id}/messages",
    response_model=List[MessageResponseDTO],
    summary="Récupérer les messages",
    description="Récupère tous les messages d'une conversation."
)
async def get_messages(
    conversation_id: str,
    limit_data: MessageLimit,
    db: Session = Depends(get_db)
):
    """Récupère les messages d'une conversation"""
    # Vérifier d'abord si la conversation existe
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    messages = conversation_service.get_messages(conversation_id, db, limit_data.limit)
    return messages

@router.put(
    "/{conversation_id}/agent",
    response_model=ConversationResponseDTO,
    summary="Mettre à jour l'agent d'une conversation",
    description="Met à jour l'agent associé à une conversation. L'agent_id peut être null pour retirer l'agent de la conversation."
)
async def update_conversation_agent(
    conversation_id: str,
    update_data: UpdateAgentDTO,
    db: Session = Depends(get_db)
):
    """Met à jour l'agent d'une conversation"""
    conversation = conversation_service.update_conversation_agent(conversation_id, update_data.agent_id, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation

@router.put(
    "/{conversation_id}/title",
    response_model=ConversationResponseDTO,
    summary="Mettre à jour le titre d'une conversation",
    description="Change le titre d'une conversation."
)
async def update_conversation_title(
    conversation_id: str,
    update_data: UpdateTitleDTO,
    db: Session = Depends(get_db)
):
    """Met à jour le titre d'une conversation"""
    if not update_data.title:
        raise HTTPException(status_code=400, detail="Le titre ne peut pas être vide")
    
    conversation = conversation_service.update_conversation_title(conversation_id, update_data.title, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation 