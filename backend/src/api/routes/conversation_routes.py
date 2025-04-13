from fastapi import APIRouter, HTTPException, Depends, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
# Correction ici: ne pas importer Message depuis le domaine mais utiliser celui de database.models
# from ...models.domain.conversation import Message, MessageRole
from ...models.domain.conversation import MessageRole
from ...database.models import Conversation, Agent, Message
from ...models.dto.conversation_dto import (
    ConversationCreateDTO,
    ConversationUpdateDTO,
    ConversationResponseDTO,
    MessageCreateDTO,
    MessageResponseDTO
)
from ...models.dto.agent_dto import AgentRequestDTO, AgentResponseRequestDTO
from ...services.conversation_service import ConversationService
from ...services.agent_service import AgentService
from ...database import get_db
from datetime import datetime
from fastapi import status

# Création du router principal
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
    metadata: Optional[Dict[str, Any]] = None

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

@router.get("", response_model=List[ConversationResponseDTO])
async def list_conversations(db: Session = Depends(get_db)):
    """Liste toutes les conversations"""
    return conversation_service.get_all_conversations(db)

@router.post("", response_model=ConversationResponseDTO)
async def create_conversation(conversation_data: ConversationCreateDTO, db: Session = Depends(get_db)):
    """Crée une nouvelle conversation"""
    return conversation_service.create_conversation(conversation_data, db)

@router.get("/{conversation_id}", response_model=ConversationResponseDTO)
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

@router.post("/{conversation_id}/messages", response_model=MessageResponseDTO)
async def add_message(
    conversation_id: str,
    message_data: MessageCreateDTO,
    db: Session = Depends(get_db)
):
    """Ajoute un message à une conversation"""
    try:
        return conversation_service.add_message(conversation_id, message_data, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put(
    "/{conversation_id}/messages",
    summary="Supprimer tous les messages",
    description="Supprime tous les messages d'une conversation spécifique.",
    responses={
        200: {
            "description": "Messages supprimés avec succès",
            "content": {
                "application/json": {
                    "example": {"message": "Tous les messages ont été supprimés avec succès"}
                }
            }
        },
        404: {
            "description": "Conversation non trouvée",
            "content": {
                "application/json": {
                    "example": {"detail": "Conversation non trouvée"}
                }
            }
        },
        500: {
            "description": "Erreur serveur",
            "content": {
                "application/json": {
                    "example": {"detail": "Une erreur est survenue lors de la suppression des messages"}
                }
            }
        }
    }
)
async def delete_all_messages(conversation_id: str, db: Session = Depends(get_db)):
    """
    Supprime tous les messages d'une conversation spécifique.
    
    Args:
        conversation_id: L'identifiant unique de la conversation
        db: La session de base de données
        
    Returns:
        Un message de confirmation si la suppression a réussi
        
    Raises:
        HTTPException 404: Si la conversation n'existe pas
        HTTPException 500: En cas d'erreur lors de la suppression
    """
    try:
        # Vérifier si la conversation existe
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation non trouvée")

        # Supprimer tous les messages de la conversation
        # Correction: Message est déjà importé correctement depuis database.models
        db.query(Message).filter(Message.conversation_id == conversation_id).delete(synchronize_session=False)
        db.commit()

        return {"message": "Tous les messages ont été supprimés avec succès"}

    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la suppression des messages : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}/messages", response_model=List[MessageResponseDTO])
async def get_messages(
    conversation_id: str,
    limit: Optional[int] = Query(None),  # Utiliser Query() au lieu de Body()
    db: Session = Depends(get_db)
):
    """Récupère les messages d'une conversation"""
    try:
        # Vérifier d'abord si la conversation existe
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation non trouvée")

        # Récupérer les messages avec la limite si spécifiée
        # Correction: utiliser directement le modèle Message de database.models
        query = db.query(Message).filter(Message.conversation_id == conversation_id)
        if limit is not None:
            query = query.limit(limit)
        messages = query.all()

        # Si aucun message n'est trouvé, retourner un tableau vide
        if not messages:
            return []

        # Convertir les messages en DTOs
        return [
            MessageResponseDTO.model_validate({
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "agent_id": msg.agent_id,
                "metadata": dict(msg.message_metadata or {})
            })
            for msg in messages
        ]
    except Exception as e:
        print(f"Erreur lors de la récupération des messages : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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

@router.delete("", response_model=dict)
async def delete_all_conversations(db: Session = Depends(get_db)):
    """Supprime toutes les conversations"""
    try:
        success = conversation_service.delete_all_conversations(db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la suppression des conversations"
            )
        return {"message": "Toutes les conversations ont été supprimées avec succès"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )