from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..database.models import Agent
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
from .conversation_service import ConversationService

class AgentService:
    _instance = None
    _llm_interface = None
    _conversation_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
            cls._instance._llm_interface = LLMInterface()
            cls._instance._conversation_service = ConversationService()
        return cls._instance

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

    def process_request(self, agent_id: str, request: AgentRequestDTO, db: Session) -> Optional[AgentResponseRequestDTO]:
        """Traite une requête avec un agent"""
        # Récupérer l'agent
        agent = self.get_agent(agent_id, db)
        if not agent or not agent.is_active:
            return None

        try:
            # Si un ID de conversation est fourni, sauvegarder le message utilisateur
            if request.conversation_id:
                user_message = MessageCreateDTO(
                    role=MessageRole.USER,
                    content=request.prompt,
                    metadata=request.parameters
                )
                self._conversation_service.add_message(request.conversation_id, user_message, db)

            # Préparer le contexte pour le modèle
            context = {
                "role": agent.role,
                "model_type": agent.model_type,
                **(agent.config or {})
            }

            # Générer la réponse avec le modèle
            response = self._llm_interface.generate_response(
                prompt=request.prompt,
                context=context,
                conversation_id=request.conversation_id
            )

            # Si un ID de conversation est fourni, sauvegarder la réponse de l'agent
            if request.conversation_id:
                assistant_message = MessageCreateDTO(
                    role=MessageRole.ASSISTANT,
                    content=response,
                    agent_id=agent_id,
                    metadata={"model_type": agent.model_type}
                )
                self._conversation_service.add_message(request.conversation_id, assistant_message, db)

            # Retourner la réponse formatée
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