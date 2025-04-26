from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..database.models import Agent, Message
from ..models.dto.agent_dto import (
    AgentCreateDTO,
    AgentUpdateDTO,
    AgentResponseDTO,
    AgentRequestDTO,
    AgentResponseRequestDTO
)
from datetime import datetime
from ..models.dto.conversation_dto import MessageCreateDTO, MessageRole
from .agent_manager import AgentManager
from .conversation_history_service import ConversationHistoryService
import asyncio
import uuid

class AgentService:
    _instance = None
    _agent_manager = None
    _history_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
            cls._instance._agent_manager = AgentManager()
            cls._instance._history_service = ConversationHistoryService()
        return cls._instance

    def __init__(self):
        # L'initialisation est maintenant dans __new__
        pass

    async def create_agent(self, agent_data: AgentCreateDTO, db: Session) -> AgentResponseDTO:
        """Crée un nouvel agent"""
        # Créer l'agent dans la base de données
        agent_id = str(uuid.uuid4())
        db_agent = Agent(
            id=agent_id,
            name=agent_data.name,
            model_type=agent_data.model_type,
            role=agent_data.role,
            config=agent_data.config,
            is_active=True
        )
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        
        # Enregistrer l'agent dans le manager
        await self._agent_manager.register_agent(
            agent_id=agent_id,
            role=agent_data.role,
            initial_context={
                "model_type": agent_data.model_type,
                "config": agent_data.config
            }
        )
        
        return AgentResponseDTO.model_validate(db_agent)

    def get_agent(self, agent_id: str, db: Session) -> Optional[AgentResponseDTO]:
        """Récupère un agent par son ID"""
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            return AgentResponseDTO.model_validate(agent)
        return None

    def get_all_agents(self, db: Session) -> List[AgentResponseDTO]:
        """Récupère tous les agents"""
        agents = db.query(Agent).all()
        return [AgentResponseDTO.model_validate(agent) for agent in agents]

    async def update_agent(self, agent_id: str, agent_data: AgentUpdateDTO, db: Session) -> Optional[AgentResponseDTO]:
        """Met à jour un agent"""
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return None

        # Mettre à jour le contexte dans le manager
        await self._agent_manager.update_agent_context(
            agent_id,
            {
                "model_type": agent_data.model_type or agent.model_type,
                "config": agent_data.config or agent.config
            }
        )

        # Mettre à jour l'agent dans la base de données
        update_data = agent_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)

        db.commit()
        db.refresh(agent)
        return AgentResponseDTO.model_validate(agent)

    async def delete_agent(self, agent_id: str, db: Session) -> bool:
        """Supprime un agent"""
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return False

        db.delete(agent)
        db.commit()
        return True

    async def process_request(self, agent_id: str, request: AgentRequestDTO, db: Session) -> AgentResponseRequestDTO:
        """
        Traite une requête pour un agent spécifique.
        
        Args:
            agent_id: L'ID de l'agent
            request: La requête à traiter
            db: La session de base de données
            
        Returns:
            La réponse de l'agent
        """
        try:
            print(f"Traitement de la requête pour l'agent {agent_id}")
            
            # Récupérer l'agent
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                print(f"Agent {agent_id} non trouvé")
                return AgentResponseRequestDTO(
                    status="error",
                    response="Agent non trouvé",
                    timestamp=datetime.now(),
                    conversation_id=request.conversation_id,
                    agent_id=agent_id
                )

            print(f"Agent trouvé : {agent.name}")

            # Vérifier si l'agent est enregistré dans le manager
            try:
                await self._agent_manager.get_agent_context(agent_id)
            except ValueError:
                # Si l'agent n'est pas enregistré, l'enregistrer
                print(f"Enregistrement de l'agent {agent_id} dans le manager")
                await self._agent_manager.register_agent(
                    agent_id=agent_id,
                    role=agent.role,
                    initial_context={
                        "model_type": agent.model_type,
                        "config": agent.config
                    }
                )

            # Soumettre la requête au manager
            request_id = await self._agent_manager.submit_request(
                agent_id=agent_id,
                prompt=request.prompt,
                priority=0,  # Priorité par défaut
                conversation_id=request.conversation_id
            )

            # Attendre la réponse
            # Note: Dans une implémentation réelle, nous devrions utiliser un système de callback
            # ou un WebSocket pour recevoir la réponse de manière asynchrone
            await asyncio.sleep(0.1)  # Attendre un peu pour la démonstration

            # Récupérer le contexte mis à jour
            context = await self._agent_manager.get_agent_context(agent_id)
            response = context["conversation_history"][-1]["content"]

            print(f"Réponse générée avec succès : {response[:100]}...")

            # Retourner la réponse
            return AgentResponseRequestDTO(
                status="success",
                response=response,
                timestamp=datetime.now(),
                conversation_id=request.conversation_id,
                agent_id=agent_id
            )

        except Exception as e:
            print(f"Erreur lors du traitement de la requête : {str(e)}")
            return AgentResponseRequestDTO(
                status="error",
                response=f"Une erreur est survenue : {str(e)}",
                timestamp=datetime.now(),
                conversation_id=request.conversation_id,
                agent_id=agent_id
            ) 