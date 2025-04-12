from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from ..database.models import Conversation, Message, Agent
from ..models.dto.conversation_dto import (
    ConversationCreateDTO,
    ConversationUpdateDTO,
    ConversationResponseDTO,
    MessageCreateDTO,
    MessageResponseDTO,
    MessageRole
)
from ..models.dto.agent_dto import AgentRequestDTO
from fastapi import HTTPException
from ..services.agent_service import AgentService

class ConversationService:
    def __init__(self):
        self._agent_service = AgentService()

    @property
    def agent_service(self):
        return self._agent_service

    def get_conversation_by_title(self, title: str, db: Session) -> Optional[ConversationResponseDTO]:
        """Récupère une conversation par son titre"""
        conversation = db.query(Conversation).filter(Conversation.title == title).first()
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

    def create_conversation(self, conversation_data: ConversationCreateDTO, db: Session) -> ConversationResponseDTO:
        """Crée une nouvelle conversation"""
        # Vérifier si une conversation avec le même titre existe déjà
        existing_conversation = self.get_conversation_by_title(conversation_data.title, db)
        if existing_conversation:
            return existing_conversation

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

    def add_message(
        self,
        conversation_id: str,
        message_data: MessageCreateDTO,
        db: Session
    ) -> MessageResponseDTO:
        """
        Ajoute un message à une conversation.
        
        Args:
            conversation_id: L'ID de la conversation
            message_data: Les données du message à ajouter
            db: La session de base de données
            
        Returns:
            Le message créé
        """
        # Vérifier si la conversation existe
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation non trouvée")

        # Créer le message
        message = Message(
            conversation_id=conversation_id,
            role=message_data.role,
            content=message_data.content,
            message_metadata=message_data.metadata
        )

        # Ajouter le message à la conversation
        conversation.messages.append(message)
        conversation.updated_at = datetime.utcnow()

        # Sauvegarder le message
        db.add(message)
        db.commit()
        db.refresh(message)

        # Si c'est un message utilisateur et qu'il y a un agent associé, envoyer la requête à l'agent de manière asynchrone
        if message.role == "user" and conversation.agent_id:
            # Utiliser une fonction asynchrone pour gérer la réponse de l'agent
            import asyncio
            asyncio.create_task(self._handle_agent_response(conversation_id, conversation.agent_id, message.content, db))

        # Retourner immédiatement le message créé
        return MessageResponseDTO(
            id=str(message.id),
            conversation_id=str(message.conversation_id),
            role=message.role,
            content=message.content,
            timestamp=message.timestamp,
            metadata=message.message_metadata
        )

    async def _handle_agent_response(self, conversation_id: str, agent_id: str, user_message: str, db: Session):
        """Gère la réponse de l'agent de manière asynchrone"""
        try:
            # Créer la requête pour l'agent
            request = AgentRequestDTO(
                prompt=user_message,
                conversation_id=conversation_id,
                parameters={}
            )

            # Traiter la requête avec l'agent
            agent_response = self.agent_service.process_request(
                agent_id,
                request,
                db
            )

            # Si la réponse est un succès, créer un nouveau message avec la réponse de l'agent
            if agent_response.status == "success":
                # Créer une nouvelle session pour la transaction
                from sqlalchemy.orm import Session
                new_db = Session(bind=db.get_bind())
                try:
                    agent_message = Message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=agent_response.response,
                        agent_id=agent_id,
                        message_metadata={"timestamp": str(agent_response.timestamp)}
                    )

                    # Ajouter le message de l'agent à la conversation
                    conversation = new_db.query(Conversation).filter(Conversation.id == conversation_id).first()
                    if conversation:
                        conversation.messages.append(agent_message)
                        conversation.updated_at = datetime.utcnow()

                        # Sauvegarder le message de l'agent
                        new_db.add(agent_message)
                        new_db.commit()
                        new_db.refresh(agent_message)
                        print(f"Message de l'agent ajouté avec succès à la conversation {conversation_id}")
                except Exception as e:
                    new_db.rollback()
                    print(f"Erreur lors de l'ajout du message de l'agent : {str(e)}")
                finally:
                    new_db.close()

        except Exception as e:
            print(f"Erreur lors du traitement par l'agent : {str(e)}")

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

    def update_conversation(self, conversation_id: str, conversation_data: ConversationUpdateDTO, db: Session) -> ConversationResponseDTO:
        """
        Met à jour une conversation existante.
        
        Args:
            conversation_id: L'ID de la conversation à mettre à jour
            conversation_data: Les données de mise à jour
            db: La session de base de données
            
        Returns:
            La conversation mise à jour
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation non trouvée")
        
        # Mise à jour des champs
        update_data = conversation_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'title':
                conversation.title = value
            elif field == 'agent_id':
                conversation.agent_id = value
            # Ne pas mettre à jour les métadonnées si elles ne sont pas fournies
        
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

    def delete_all_conversations(self, db: Session) -> bool:
        """
        Supprime toutes les conversations de la base de données.
        
        Args:
            db: La session de base de données
            
        Returns:
            True si la suppression a réussi
        """
        try:
            # Supprimer toutes les conversations (les messages seront supprimés en cascade)
            db.query(Conversation).delete()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Erreur lors de la suppression des conversations : {str(e)}")
            return False 