from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..database.models import Message
from ..models.domain.conversation import MessageRole

class ConversationHistoryService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationHistoryService, cls).__new__(cls)
        return cls._instance

    def get_conversation_history(self, conversation_id: str, limit: int = 5, db: Session = None) -> List[Dict[str, Any]]:
        """
        Récupère l'historique d'une conversation sous forme de liste de messages.
        
        Args:
            conversation_id: ID de la conversation
            limit: Nombre maximum de messages à récupérer
            db: Session de base de données
            
        Returns:
            Liste des messages au format dictionnaire
        """
        if not db:
            return []

        # Récupérer les messages utilisateur uniquement
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == MessageRole.USER
        ).order_by(Message.timestamp.desc()).limit(limit).all()

        # Convertir en format dictionnaire et inverser l'ordre pour avoir l'ordre chronologique
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in reversed(messages)
        ] 