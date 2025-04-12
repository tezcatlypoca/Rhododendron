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
from .llm_interface import LLMInterface
from .conversation_history_service import ConversationHistoryService

class AgentService:
    _instance = None
    _llm_interface = None
    _history_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
            cls._instance._llm_interface = LLMInterface()
            cls._instance._history_service = ConversationHistoryService()
        return cls._instance

    def __init__(self):
        # L'initialisation est maintenant dans __new__
        pass

    def create_agent(self, agent_data: AgentCreateDTO, db: Session) -> AgentResponseDTO:
        """Crée un nouvel agent"""
        db_agent = Agent(
            name=agent_data.name,
            model_type=agent_data.model_type,
            role=agent_data.role,
            config=agent_data.config,
            is_active=True  # Par défaut, l'agent est actif
        )
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
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

    def update_agent(self, agent_id: str, agent_data: AgentUpdateDTO, db: Session) -> Optional[AgentResponseDTO]:
        """Met à jour un agent"""
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return None

        update_data = agent_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)

        db.commit()
        db.refresh(agent)
        return AgentResponseDTO.model_validate(agent)

    def delete_agent(self, agent_id: str, db: Session) -> bool:
        """Supprime un agent"""
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return False

        db.delete(agent)
        db.commit()
        return True

    def process_request(self, agent_id: str, request: AgentRequestDTO, db: Session) -> AgentResponseRequestDTO:
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

            # Récupérer l'historique de la conversation si nécessaire
            conversation_history = None
            if request.conversation_id:
                print(f"Récupération de l'historique pour la conversation {request.conversation_id}")
                conversation_history = self._history_service.get_conversation_history(
                    request.conversation_id,
                    limit=5,
                    db=db
                )

            # Préparer le contexte pour le LLM
            context = {
                "role": agent.role,
                "model_type": agent.model_type,
                "parameters": request.parameters or {}
            }

            print(f"Génération de la réponse pour le prompt : {request.prompt}")
            # Générer la réponse avec le LLM
            response = self._llm_interface.generate_response(
                prompt=request.prompt,
                context=context,
                conversation_history=conversation_history
            )

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