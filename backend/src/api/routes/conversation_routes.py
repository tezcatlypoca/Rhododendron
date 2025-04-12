from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ...models.conversation import Conversation, Message, MessageRole
from ...models.dto.agent_dto import AgentRequestDTO, AgentResponseRequestDTO
from ...services.llm_interface import LLMInterface
from ...services.conversation_service import ConversationService
from ...services.agent_service import AgentService
from datetime import datetime

router = APIRouter()
llm_interface = LLMInterface()
conversation_service = ConversationService()
agent_service = AgentService()

@router.post("/conversations", response_model=Conversation)
async def create_conversation(title: str, agent_id: Optional[str] = None):
    """Crée une nouvelle conversation avec un agent optionnel"""
    conversation = conversation_service.create_conversation(title)
    if agent_id:
        agent = agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent non trouvé")
        conversation.agent_id = agent_id
        conversation_service._save_conversation(conversation)
    return conversation

@router.get("/conversations", response_model=List[Conversation])
async def get_all_conversations():
    """Récupère toutes les conversations"""
    return conversation_service.get_all_conversations()

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Récupère une conversation spécifique"""
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(conversation_id: str, limit: Optional[int] = None):
    """Récupère les messages d'une conversation"""
    messages = conversation_service.get_messages(conversation_id, limit)
    if not messages:
        raise HTTPException(status_code=404, detail="Aucun message trouvé")
    return messages

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def add_message(conversation_id: str, message: Message):
    """Ajoute un message à une conversation"""
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    updated_conversation = conversation_service.add_message(conversation_id, message)
    if not updated_conversation:
        raise HTTPException(status_code=500, detail="Erreur lors de l'ajout du message")
    
    return message

@router.post("/conversations/{conversation_id}/send", response_model=Message)
async def send_message(conversation_id: str, request: AgentRequestDTO):
    """Envoie un message dans une conversation et obtient la réponse de l'agent"""
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    if not conversation.agent_id:
        raise HTTPException(status_code=400, detail="Aucun agent associé à cette conversation")
    
    # Créer et sauvegarder le message de l'utilisateur
    user_message = Message(
        role=MessageRole.USER,
        content=request.prompt
    )
    conversation_service.add_message(conversation_id, user_message)
    
    # Récupérer l'agent
    agent = agent_service.get_agent(conversation.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    
    # Générer la réponse avec le contexte de la conversation
    response = llm_interface.generate_response(
        prompt=request.prompt,
        context={
            "role": agent.role,
            "model_type": agent.model_type,
            **agent.configuration
        },
        conversation_id=conversation_id
    )
    
    # Créer et sauvegarder la réponse de l'agent
    agent_message = Message(
        role=MessageRole.ASSISTANT,
        content=response,
        agent_id=conversation.agent_id
    )
    conversation_service.add_message(conversation_id, agent_message)
    
    return agent_message

@router.delete("/conversations/{conversation_id}/messages/{message_id}")
async def delete_message(conversation_id: str, message_id: str):
    """Supprime un message d'une conversation"""
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    # Trouver et supprimer le message
    message_to_remove = None
    for message in conversation.messages:
        if message.id == message_id:
            message_to_remove = message
            break
    
    if not message_to_remove:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    
    conversation.messages.remove(message_to_remove)
    conversation_service._save_conversation(conversation)
    
    return {"status": "success", "message": "Message supprimé"}

@router.put("/conversations/{conversation_id}/title", response_model=Conversation)
async def update_conversation_title(conversation_id: str, new_title: str):
    """Met à jour le titre d'une conversation"""
    conversation = conversation_service.update_conversation_title(conversation_id, new_title)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation

@router.put("/conversations/{conversation_id}/agent", response_model=Conversation)
async def update_conversation_agent(conversation_id: str, agent_id: str):
    """Met à jour l'agent associé à une conversation"""
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    agent = agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    
    conversation.agent_id = agent_id
    conversation_service._save_conversation(conversation)
    return conversation

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Supprime une conversation"""
    success = conversation_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return {"status": "success", "message": "Conversation supprimée"} 