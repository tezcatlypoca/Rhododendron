from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from src.models.domain.agent import Agent
from src.models.dto.agent_dto import AgentCreateDTO, AgentUpdateDTO, AgentResponseDTO, AgentRequestDTO, AgentResponseRequestDTO
from src.services.llm_interface import LLMInterface

class AgentService:
    def __init__(self):
        self._agents: dict[str, Agent] = {}
        self._llm = LLMInterface()

    def create_agent(self, agent_dto: AgentCreateDTO) -> AgentResponseDTO:
        agent = Agent(
            name=agent_dto.name,
            model_type=agent_dto.model_type,
            config=agent_dto.config
        )
        self._agents[agent.id] = agent
        return self._to_response_dto(agent)

    def get_agent(self, agent_id: str) -> Optional[AgentResponseDTO]:
        agent = self._agents.get(agent_id)
        if agent:
            return self._to_response_dto(agent)
        return None

    def update_agent(self, agent_id: str, agent_dto: AgentUpdateDTO) -> Optional[AgentResponseDTO]:
        agent = self._agents.get(agent_id)
        if not agent:
            return None

        if agent_dto.name is not None:
            agent.name = agent_dto.name
        if agent_dto.model_type is not None:
            agent.model_type = agent_dto.model_type
        if agent_dto.is_active is not None:
            agent.is_active = agent_dto.is_active
        if agent_dto.config is not None:
            agent.update_config(agent_dto.config)

        return self._to_response_dto(agent)

    def process_request(self, agent_id: str, request_dto: AgentRequestDTO) -> Optional[AgentResponseRequestDTO]:
        agent = self._agents.get(agent_id)
        if not agent or not agent.is_active:
            return None

        # Construction du contexte de l'agent
        context = {
            "role": agent.config.get("role", "assistant"),
            "name": agent.name,
            **agent.config
        }

        # Utilisation de l'interface LLM pour générer la réponse
        response = self._llm.generate_response(request_dto.prompt, context)
        
        # Mise à jour de la date de dernière utilisation
        agent.last_used = datetime.now()

        return AgentResponseRequestDTO(
            status="success",
            response=response,
            timestamp=datetime.now()
        )

    def list_agents(self) -> List[AgentResponseDTO]:
        return [self._to_response_dto(agent) for agent in self._agents.values()]

    def _to_response_dto(self, agent: Agent) -> AgentResponseDTO:
        return AgentResponseDTO(
            id=agent.id,
            name=agent.name,
            model_type=agent.model_type,
            is_active=agent.is_active,
            created_at=agent.created_at,
            last_used=agent.last_used,
            config=agent.config
        ) 