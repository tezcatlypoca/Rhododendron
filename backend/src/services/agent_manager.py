from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime
import uuid
from collections import defaultdict
import logging
from .llm_interface import LLMInterface

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentContext:
    def __init__(self, agent_id: str, role: str, initial_context: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.role = role
        self.context = initial_context or {}
        self.conversation_history: List[Dict[str, str]] = []
        self.last_used: datetime = datetime.now()
        self.priority: int = 0  # Priorité par défaut

class AgentManager:
    _instance = None
    _lock = asyncio.Lock()
    _request_queue = asyncio.PriorityQueue()
    _agent_contexts: Dict[str, AgentContext] = {}
    _response_cache: Dict[str, str] = {}
    _llm_interface = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentManager, cls).__new__(cls)
            cls._instance._llm_interface = LLMInterface()
        return cls._instance

    async def register_agent(self, agent_id: str, role: str, initial_context: Dict[str, Any] = None) -> str:
        """
        Enregistre un nouvel agent avec son contexte initial.
        
        Args:
            agent_id: L'ID de l'agent dans la base de données
            role: Le rôle de l'agent
            initial_context: Le contexte initial de l'agent
            
        Returns:
            L'ID de l'agent
        """
        self._agent_contexts[agent_id] = AgentContext(agent_id, role, initial_context)
        logger.info(f"Agent {agent_id} enregistré avec le rôle {role}")
        return agent_id

    async def submit_request(
        self,
        agent_id: str,
        prompt: str,
        priority: int = 0,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Soumet une requête à l'agent spécifié.
        
        Args:
            agent_id: L'ID de l'agent
            prompt: Le prompt à traiter
            priority: La priorité de la requête (plus bas = plus prioritaire)
            conversation_id: L'ID de la conversation associée
            
        Returns:
            L'ID de la requête
        """
        if agent_id not in self._agent_contexts:
            raise ValueError(f"Agent {agent_id} non trouvé")

        request_id = str(uuid.uuid4())
        await self._request_queue.put((priority, request_id, agent_id, prompt, conversation_id))
        logger.info(f"Requête {request_id} soumise pour l'agent {agent_id}")
        return request_id

    async def _process_queue(self):
        """
        Traite la file d'attente des requêtes.
        """
        while True:
            try:
                priority, request_id, agent_id, prompt, conversation_id = await self._request_queue.get()
                
                async with self._lock:
                    # Vérifier le cache
                    cache_key = f"{agent_id}:{prompt}"
                    if cache_key in self._response_cache:
                        logger.info(f"Utilisation du cache pour la requête {request_id}")
                        response = self._response_cache[cache_key]
                    else:
                        # Obtenir le contexte de l'agent
                        agent_context = self._agent_contexts[agent_id]
                        
                        # Générer la réponse
                        response = self._llm_interface.generate_response(
                            prompt=prompt,
                            context={
                                "role": agent_context.role,
                                "conversation_id": conversation_id,
                                **agent_context.context
                            },
                            conversation_history=agent_context.conversation_history
                        )
                        
                        # Mettre en cache
                        self._response_cache[cache_key] = response
                    
                    # Mettre à jour le contexte
                    self._update_agent_context(agent_id, prompt, response, conversation_id)
                    
                    # Marquer la requête comme terminée
                    self._request_queue.task_done()
                    
            except Exception as e:
                logger.error(f"Erreur lors du traitement de la requête {request_id}: {str(e)}")
                self._request_queue.task_done()

    def _update_agent_context(
        self,
        agent_id: str,
        prompt: str,
        response: str,
        conversation_id: Optional[str]
    ):
        """
        Met à jour le contexte de l'agent après une réponse.
        """
        agent_context = self._agent_contexts[agent_id]
        agent_context.last_used = datetime.now()
        
        # Ajouter à l'historique
        agent_context.conversation_history.append({
            "role": "user",
            "content": prompt,
            "conversation_id": conversation_id
        })
        agent_context.conversation_history.append({
            "role": "assistant",
            "content": response,
            "conversation_id": conversation_id
        })
        
        # Limiter la taille de l'historique
        if len(agent_context.conversation_history) > 10:
            agent_context.conversation_history = agent_context.conversation_history[-10:]

    async def get_agent_context(self, agent_id: str) -> Dict[str, Any]:
        """
        Récupère le contexte d'un agent.
        """
        if agent_id not in self._agent_contexts:
            raise ValueError(f"Agent {agent_id} non trouvé")
        
        context = self._agent_contexts[agent_id]
        return {
            "agent_id": context.agent_id,
            "role": context.role,
            "context": context.context,
            "last_used": context.last_used,
            "conversation_history": context.conversation_history
        }

    async def update_agent_context(self, agent_id: str, new_context: Dict[str, Any]):
        """
        Met à jour le contexte d'un agent.
        """
        if agent_id not in self._agent_contexts:
            raise ValueError(f"Agent {agent_id} non trouvé")
        
        self._agent_contexts[agent_id].context.update(new_context)
        logger.info(f"Contexte de l'agent {agent_id} mis à jour")

    async def start(self):
        """
        Démarre le traitement de la file d'attente.
        """
        asyncio.create_task(self._process_queue())
        logger.info("AgentManager démarré")

    async def stop(self):
        """
        Arrête le traitement de la file d'attente.
        """
        await self._request_queue.join()
        logger.info("AgentManager arrêté") 