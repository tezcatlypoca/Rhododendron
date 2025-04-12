from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from ..database.models import Conversation, Message, Agent
from ..models.dto.conversation_dto import (
    ConversationCreateDTO,
    ConversationUpdateDTO,
    ConversationResponseDTO,
    MessageCreateDTO,
    MessageResponseDTO
)

class ConversationService:
    def create_conversation(self, conversation_data: ConversationCreateDTO, db: Session) -> ConversationResponseDTO:
        """Crée une nouvelle conversation"""
        conversation = Conversation(
            title=conversation_data.title,
            agent_id=conversation_data.agent_id,
            conversation_metadata=dict(conversation_data.metadata or {})  # Conversion explicite en dict
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        # Création d'un dictionnaire avec les données de la conversation
        conversation_dict = {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "agent_id": conversation.agent_id,
            "metadata": dict(conversation.conversation_metadata or {}),  # Conversion explicite en dict
            "messages": []  # Liste vide pour une nouvelle conversation
        }
        
        return ConversationResponseDTO.model_validate(conversation_dict)

    def get_conversation(self, conversation_id: str, db: Session) -> Optional[ConversationResponseDTO]:
        """Récupère une conversation par son ID"""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation_dict = {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "agent_id": conversation.agent_id,
                "metadata": dict(conversation.conversation_metadata or {}),
                "messages": [
                    {
                        "id": msg.id,
                        "conversation_id": msg.conversation_id,
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "agent_id": msg.agent_id,
                        "metadata": dict(msg.message_metadata or {})
                    }
                    for msg in conversation.messages
                ]
            }
            return ConversationResponseDTO.model_validate(conversation_dict)
        return None

    def get_all_conversations(self, db: Session) -> List[ConversationResponseDTO]:
        """Récupère toutes les conversations"""
        conversations = db.query(Conversation).all()
        return [
            ConversationResponseDTO.model_validate({
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "agent_id": conv.agent_id,
                "metadata": dict(conv.conversation_metadata or {}),
                "messages": [
                    {
                        "id": msg.id,
                        "conversation_id": msg.conversation_id,
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "agent_id": msg.agent_id,
                        "metadata": dict(msg.message_metadata or {})
                    }
                    for msg in conv.messages
                ]
            })
            for conv in conversations
        ]

    def add_message(self, conversation_id: str, message_data: MessageCreateDTO, db: Session) -> Optional[MessageResponseDTO]:
        """Ajoute un message à une conversation"""
        try:
            # Récupérer la conversation pour obtenir son agent_id
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                return None

            # Créer le message
            message = Message(
                conversation_id=conversation_id,
                role=message_data.role,
                content=message_data.content,
                agent_id=conversation.agent_id,  # Utiliser l'agent_id de la conversation
                message_metadata=message_data.metadata or {}
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            # Mettre à jour la date de modification de la conversation
            conversation.updated_at = datetime.now()
            db.commit()
            
            return MessageResponseDTO.model_validate({
                "id": message.id,
                "conversation_id": message.conversation_id,
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp,
                "agent_id": message.agent_id,
                "metadata": dict(message.message_metadata or {})
            })
            
        except Exception as e:
            db.rollback()
            print(f"Erreur lors de l'ajout du message : {str(e)}")
            raise

    def get_messages(self, conversation_id: str, db: Session, limit: Optional[int] = None) -> List[MessageResponseDTO]:
        """Récupère les messages d'une conversation"""
        try:
            # Vérifier d'abord si la conversation existe
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                return None

            # Récupérer les messages avec la limite si spécifiée
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
            raise

    def delete_conversation(self, conversation_id: str, db: Session) -> bool:
        """Supprime une conversation"""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False

    def update_conversation(self, conversation_id: str, conversation_data: ConversationUpdateDTO, db: Session) -> Optional[ConversationResponseDTO]:
        """Met à jour une conversation"""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return None

        update_data = conversation_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(conversation, key, value)
        
        conversation.updated_at = datetime.now()
        db.commit()
        db.refresh(conversation)
        return ConversationResponseDTO.model_validate(conversation)

    def update_conversation_agent(self, conversation_id: str, agent_id: Optional[str], db: Session) -> Optional[ConversationResponseDTO]:
        """Met à jour l'agent d'une conversation"""
        try:
            # Vérifier que l'agent existe si un agent_id est fourni
            if agent_id is not None:
                agent = db.query(Agent).filter(Agent.id == agent_id).first()
                if not agent:
                    raise ValueError(f"Agent avec l'ID {agent_id} non trouvé")

            # Récupérer la conversation avec FOR UPDATE pour verrouiller la ligne
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                return None

            # Mettre à jour l'agent_id
            conversation.agent_id = agent_id
            conversation.updated_at = datetime.now()
            
            # Forcer le flush pour détecter les erreurs potentielles
            db.flush()
            
            # Valider la transaction
            db.commit()
            
            # Recharger l'objet depuis la base de données
            db.refresh(conversation)

            # Vérifier que la mise à jour a bien été effectuée
            if conversation.agent_id != agent_id:
                raise Exception("La mise à jour de l'agent_id a échoué")

            # Création d'un dictionnaire avec les données de la conversation
            conversation_dict = {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "agent_id": conversation.agent_id,  # Devrait maintenant être le nouvel agent_id
                "metadata": dict(conversation.conversation_metadata or {}),
                "messages": [
                    {
                        "id": msg.id,
                        "conversation_id": msg.conversation_id,
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "agent_id": msg.agent_id,
                        "metadata": dict(msg.message_metadata or {})
                    }
                    for msg in conversation.messages
                ]
            }
            
            return ConversationResponseDTO.model_validate(conversation_dict)
            
        except ValueError as ve:
            # En cas d'erreur de validation (agent non trouvé)
            db.rollback()
            print(f"Erreur de validation lors de la mise à jour de l'agent : {str(ve)}")
            raise
        except Exception as e:
            # En cas d'erreur, annuler la transaction
            db.rollback()
            print(f"Erreur lors de la mise à jour de l'agent : {str(e)}")
            raise

    def update_conversation_title(self, conversation_id: str, title: str, db: Session) -> Optional[ConversationResponseDTO]:
        """Met à jour le titre d'une conversation"""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return None

        conversation.title = title
        conversation.updated_at = datetime.now()
        db.commit()
        db.refresh(conversation)

        # Création d'un dictionnaire avec les données de la conversation
        conversation_dict = {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "agent_id": conversation.agent_id,
            "metadata": dict(conversation.conversation_metadata or {}),
            "messages": [
                {
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "agent_id": msg.agent_id,
                    "metadata": dict(msg.message_metadata or {})
                }
                for msg in conversation.messages
            ]
        }
        
        return ConversationResponseDTO.model_validate(conversation_dict) 