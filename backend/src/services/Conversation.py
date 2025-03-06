from datetime import date
from typing import List, Optional
from Agent import Agent
from src.dto.dto_message import MessageDTO
from src.dto.dto_conversation import ConversationDTO
import uuid

"""
Classe métier représentant une conversation entre différents participants.
"""
class Conversation:
    
    """
    Initialise une nouvelle instance de Conversation.
    
    Args:
        conversation_id: Identifiant unique de la conversation
        timestamp: Date de création de la conversation
        context: Contexte de la conversation
        project_id: Identifiant du projet associé
        messages: Liste des messages de la conversation
        participants: Liste des participants à la conversation
        status: Statut de la conversation ('initial', 'draft', 'active', 'archived')
    """
    def __init__(self, conversation_id: str = None, timestamp: date = None, context: str = None, project_id: int = None, 
                 messages: Optional[List[MessageDTO]] = None, 
                 participants: Optional[List[Agent]] = None,
                 status: str = 'initial'):
        self.id = conversation_id
        self.timestamp = timestamp
        self.context = context
        self.project_id = project_id
        self.messages = messages or []
        self.participants = participants or []
        self.status = status
    # END FUNCTION
    
    """
    Ajoute un message à la conversation.
    
    Args:
        message: Le message à ajouter
    """
    def add_message(self, message: MessageDTO) -> None:
        pass
    # END FUNCTION
    
    """
    Ajoute un participant à la conversation.
    
    Args:
        participant: Le participant à ajouter
    """
    def add_participant(self, participant: Agent) -> None:
        pass
    # END FUNCTION
    
    """
    Retire un participant de la conversation.
    
    Args:
        participant_id: L'identifiant du participant à retirer
        
    Returns:
        bool: True si le participant a été retiré, False sinon
    """
    def remove_participant(self, participant_id: str) -> bool:
        pass
    # END FUNCTION
    
    """
    Change le statut de la conversation.
    
    Args:
        new_status: Le nouveau statut ('initial', 'draft', 'active', 'archived')
        
    Returns:
        bool: True si le statut a été changé, False sinon
    """
    def change_status(self, new_status: str) -> bool:
        pass
    # END FUNCTION
    
    """
    Récupère tous les messages d'un participant spécifique.
    
    Args:
        participant_id: L'identifiant du participant
        
    Returns:
        List[MessageDTO]: La liste des messages du participant
    """
    def get_messages_by_participant(self, participant_id: str) -> List[MessageDTO]:
        pass
    # END FUNCTION
    
    """
    Récupère tous les messages dans une plage de dates.
    
    Args:
        start_date: Date de début de la plage
        end_date: Date de fin de la plage
        
    Returns:
        List[MessageDTO]: La liste des messages dans la plage de dates
    """
    def get_messages_by_date_range(self, start_date: date, end_date: date) -> List[MessageDTO]:
        pass
    # END FUNCTION
    
    """
    Convertit l'objet métier Conversation en DTO.
    
    Returns:
        ConversationDTO: Le DTO représentant cette conversation
    """
    def to_dto(self) -> ConversationDTO:
        pass
    # END FUNCTION
    
    """
    Crée une instance de Conversation à partir d'un DTO.
    
    Args:
        dto: Le DTO à convertir
        
    Returns:
        Conversation: Une nouvelle instance de Conversation
    """
    @classmethod
    def from_dto(cls, dto: ConversationDTO) -> 'Conversation':
        pass
    # END FUNCTION
    
    """
    Archive la conversation.
    
    Returns:
        bool: True si la conversation a été archivée, False sinon
    """
    def archive(self) -> bool:
        pass
    # END FUNCTION
    
    """
    Vérifie si la conversation est active.
    
    Returns:
        bool: True si la conversation est active, False sinon
    """
    def is_active(self) -> bool:
        pass
    # END FUNCTION
    
    """
    Obtient le nombre de participants à la conversation.
    
    Returns:
        int: Le nombre de participants
    """
    def get_participant_count(self) -> int:
        pass
    # END FUNCTION
    
    """
    Obtient le nombre de messages dans la conversation.
    
    Returns:
        int: Le nombre de messages
    """
    def get_message_count(self) -> int:
        pass
    # END FUNCTION

    ######## UTILS ########

    def set_id(self, id: uuid.UUID):
        pass

    def set_timestamp(self, time: date):
        pass

    def set_context(self, context: str):
        pass

    def set_project_id(self, projectId: uuid.UUID):
        pass

    def generate_id(self) -> uuid.UUID:
        return uuid.uuid4()
# END CLASS