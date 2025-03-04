from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict, Optional
import os, json, sys, requests, streamlit as st

# Ajouter le chemin racine du projet au PYTHONPATH
# Cela suppose que vous êtes dans src/agents/Agent.py
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(root_dir)

# Maintenant vous pouvez importer
from src.dto.dto_role import *

class Agent:
    """
        Initialise un agent AI.
        
        Args:
            name: Nom unique de l'agent
            role: Rôle de l'agent (Manager, Developer, Tester)
            model_name: Nom du modèle LLM local à utiliser (ex: "llama3:8b")
            system_prompt: Prompt système qui définit le comportement de l'agent
            api_url: URL de l'API Ollama
    """
    def __init__(self, name: str, role: Role, model_name: str, temperature: float = 0.7):
        self.name = name
        self.role = role
        self.model_name = model_name
        self.temperature = temperature
        self.model = self.charger_llm(self.temperature)
        self.conversation_history = []
        self.memory = {}
    # END FUNCTION
    
    """
        Envoie une requête au modèle LLM local et retourne la réponse.
        
        Args:
            user_message: Message à envoyer au LLM
            temperature: Paramètre de température pour l'inférence
            
        Returns:
            La réponse du modèle LLM
    """
    def query(self, user_message: str) -> str:
        # Construire le contexte complet avec l'historique
        context = self._build_context(user_message)
        prompt_user = PromptTemplate.from_template(context)
        
        # Préparer la requête pour Ollama
        # payload = {
        #     "model": self.model_name,
        #     "prompt": context,
        #     "temperature": self.temperature,
        #     "stream": False
        # }
        
        # Appeler le model choisi afin de lui adresser une requête
        try:
            response = self.model.invoke(context)
        
            # Mettre à jour l'historique de conversation
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            return response
        except Exception as e:
            return {'DEBUG': 'ERROR', 'MESSAGE': f"Erreur lors de la requête au modèle: {str(e)}"}
    # END FUNCTION
    
    """
    Construit le contexte complet pour la requête en incluant:
    - Le prompt système
    - L'historique de conversation
    - La requête actuelle
    
    Returns:
        Le contexte complet pour le LLM
    """
    def _build_context(self, current_query: str) -> str:
        context = f"{self.role.prompt_system}\n\n"
        
        # Ajouter l'historique de conversation pertinent (limité pour éviter de dépasser le contexte)
        for message in self.conversation_history[-10:]:  # Limiter à 10 messages
            if message["role"] == "user":
                context += f"Human: {message['content']}\n"
            else:
                context += f"Assistant: {message['content']}\n"
        
        # Ajouter la requête actuelle
        context += f"Human: {current_query}\nAssistant:"
        
        return context
    # END FUNCTION
    
    def add_to_memory(self, key: str, value: any) -> None:
        """
        Ajoute ou met à jour une information dans la mémoire de l'agent.
        """
        self.memory[key] = value
    # END FUNCTION
    
    def get_from_memory(self, key: str) -> Optional[any]:
        """
        Récupère une information de la mémoire de l'agent.
        """
        return self.memory.get(key)
    # END FUNCTION
    
    def clear_conversation(self) -> None:
        """
        Efface l'historique de conversation.
        """
        self.conversation_history = []
    # END FUNCTION
    
    # @st.cache_resource
    def charger_llm(self, temperature):
        """Charge le modèle LLM avec Ollama."""
        return Ollama(model=self.model_name, temperature=temperature)
    # END FUNCTION
    
# END CLASS

# if __name__ == "__main__":
#     # dev_agent = Agent(name="Test", role=DeveloperDTO(), model_name="codellama:7b-instruct-q4_0", temperature=0.7)
#     # response = dev_agent.query("Comment gérer des conflits entre collègues ? En français")
#     # print(response)
#     print("coucou")