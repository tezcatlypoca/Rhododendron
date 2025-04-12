from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ...models.conversation import Conversation, Message, MessageRole
from ...models.dto.agent_dto import AgentRequestDTO, AgentResponseRequestDTO
from ...services.llm_interface import LLMInterface
from ...services.conversation_service import ConversationService
from ...services.agent_service import AgentService
from datetime import datetime

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={404: {"description": "Non trouvé"}},
)

llm_interface = LLMInterface()
conversation_service = ConversationService()
agent_service = AgentService()

class ConversationCreate(BaseModel):
    title: str
    agent_id: Optional[str] = None

@router.post("", response_model=Conversation, summary="Créer une nouvelle conversation")
async def create_conversation(conversation: ConversationCreate):
    """
    Crée une nouvelle conversation avec un titre et un agent optionnel.
    
    Args:
        conversation (ConversationCreate): Les données de la conversation à créer
        
    Returns:
        Conversation: La conversation créée
        
    Raises:
        HTTPException: Si l'agent spécifié n'existe pas
    """
    new_conversation = conversation_service.create_conversation(conversation.title)
    if conversation.agent_id:
        agent = agent_service.get_agent(conversation.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent non trouvé")
        new_conversation.agent_id = conversation.agent_id
        conversation_service._save_conversation(new_conversation)
    return new_conversation

@router.get("", response_model=List[Conversation], summary="Lister toutes les conversations")
async def get_all_conversations():
    """
    Récupère la liste de toutes les conversations existantes.
    
    Returns:
        List[Conversation]: Liste des conversations
    """
    return conversation_service.get_all_conversations()

@router.get("/{conversation_id}", response_model=Conversation, summary="Obtenir une conversation")
async def get_conversation(conversation_id: str):
    """
    Récupère les détails d'une conversation spécifique.
    
    Args:
        conversation_id (str): L'ID de la conversation à récupérer
        
    Returns:
        Conversation: Les détails de la conversation
        
    Raises:
        HTTPException: Si la conversation n'existe pas
    """
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation

@router.get("/{conversation_id}/messages", response_model=List[Message], summary="Obtenir les messages d'une conversation")
async def get_conversation_messages(conversation_id: str, limit: Optional[int] = None):
    """
    Récupère les messages d'une conversation, avec une limite optionnelle.
    
    Args:
        conversation_id (str): L'ID de la conversation
        limit (Optional[int]): Nombre maximum de messages à récupérer
        
    Returns:
        List[Message]: Liste des messages de la conversation
        
    Raises:
        HTTPException: Si la conversation n'existe pas ou ne contient pas de messages
    """
    messages = conversation_service.get_messages(conversation_id, limit)
    if not messages:
        raise HTTPException(status_code=404, detail="Aucun message trouvé")
    return messages

@router.post("/{conversation_id}/messages", response_model=Message, summary="Ajouter un message")
async def add_message(conversation_id: str, message: Message):
    """
    Ajoute un nouveau message à une conversation existante.
    
    Args:
        conversation_id (str): L'ID de la conversation
        message (Message): Le message à ajouter
        
    Returns:
        Message: Le message ajouté
        
    Raises:
        HTTPException: Si la conversation n'existe pas ou si l'ajout échoue
    """
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    updated_conversation = conversation_service.add_message(conversation_id, message)
    if not updated_conversation:
        raise HTTPException(status_code=500, detail="Erreur lors de l'ajout du message")
    
    return message

@router.post("/{conversation_id}/send", response_model=Message, summary="Envoyer un message et obtenir une réponse")
async def send_message(conversation_id: str, request: AgentRequestDTO):
    """
    Envoie un message dans une conversation et obtient la réponse de l'agent associé.
    
    Args:
        conversation_id (str): L'ID de la conversation
        request (AgentRequestDTO): Le message à envoyer
        
    Returns:
        Message: La réponse de l'agent
        
    Raises:
        HTTPException: Si la conversation n'existe pas, n'a pas d'agent associé, ou si l'agent n'existe pas
    """
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

@router.delete("/{conversation_id}/messages/{message_id}", summary="Supprimer un message")
async def delete_message(conversation_id: str, message_id: str):
    """
    Supprime un message spécifique d'une conversation.
    
    Args:
        conversation_id (str): L'ID de la conversation
        message_id (str): L'ID du message à supprimer
        
    Returns:
        dict: Statut de la suppression
        
    Raises:
        HTTPException: Si la conversation ou le message n'existe pas
    """
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

@router.put("/{conversation_id}/title", response_model=Conversation, summary="Mettre à jour le titre")
async def update_conversation_title(conversation_id: str, new_title: str):
    """
    Met à jour le titre d'une conversation existante.
    
    Args:
        conversation_id (str): L'ID de la conversation
        new_title (str): Le nouveau titre
        
    Returns:
        Conversation: La conversation mise à jour
        
    Raises:
        HTTPException: Si la conversation n'existe pas
    """
    conversation = conversation_service.update_conversation_title(conversation_id, new_title)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation

@router.put("/{conversation_id}/agent", response_model=Conversation, summary="Mettre à jour l'agent")
async def update_conversation_agent(conversation_id: str, agent_id: str):
    """
    Change l'agent associé à une conversation.
    
    Args:
        conversation_id (str): L'ID de la conversation
        agent_id (str): L'ID du nouvel agent
        
    Returns:
        Conversation: La conversation mise à jour
        
    Raises:
        HTTPException: Si la conversation ou l'agent n'existe pas
    """
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    agent = agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    
    conversation.agent_id = agent_id
    conversation_service._save_conversation(conversation)
    return conversation

@router.delete("/{conversation_id}", summary="Supprimer une conversation")
async def delete_conversation(conversation_id: str):
    """
    Supprime une conversation et tous ses messages.
    
    Args:
        conversation_id (str): L'ID de la conversation à supprimer
        
    Returns:
        dict: Statut de la suppression
        
    Raises:
        HTTPException: Si la conversation n'existe pas
    """
    success = conversation_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return {"status": "success", "message": "Conversation supprimée"} 