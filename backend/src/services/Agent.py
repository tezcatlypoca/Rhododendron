from typing import Optional
from src.dto.dto_role import RoleDTO
from src.dto.dto_agent import agentDTO
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

"""
Classe métier représentant un agent avec un nom, un rôle, un modèle et une température.
"""
class Agent:
    
    """
    Initialise une nouvelle instance d'Agent.
    
    Args:
        name: Nom de l'agent
        role: Rôle de l'agent
        model_name: Nom du modèle utilisé par l'agent
        temperature: Paramètre de température pour les générations de l'agent
    """
    def __init__(self, name: str, role: RoleDTO, model_name: str, temperature: float):
        self.name = name
        self.role = role
        self.model_name = model_name
        self.temperature = temperature
        self.model = self.charge_llm(self.model_name)
    # END FUNCTION

    """
        Envoie une requête au modèle LLM local et retourne la réponse.
        
        Args:
            user_message: Message à envoyer au LLM
            temperature: Paramètre de température pour l'inférence
            
        Returns:
            La réponse du modèle LLM
    """
    def query(self, context: str) -> str:        
        try:
            response = self.model.invoke(context)
            
            return response
        except Exception as e:
            return {'DEBUG': 'ERROR', 'MESSAGE': f"Erreur lors de la requête au modèle: {str(e)}"}
    # END FUNCTION

    """
    Charge le modèle llm initialisé au moment de 'linstanciation de la classe

    Args:
        température: paramètre de créativité du llm
    Returns:
        Object Ollama model
    """
    def charger_llm(self, temperature):
        """Charge le modèle LLM avec Ollama."""
        return Ollama(model=self.model_name, temperature=temperature)
    # END FUNCTION
    
    """
    Modifie le nom de l'agent
    
    Args:
        name: Nouveau nom de l'agent
        
    Returns:
        bool: True si le nom a été modifié, False sinon
    """
    def set_name(self, name: str) -> bool:
        pass
    # END FUNCTION
    
    """
    Modifie le rôle de l'agent
    
    Args:
        role: Nouveau rôle de l'agent
        
    Returns:
        bool: True si le rôle a été modifié, False sinon
    """
    def set_role(self, role: RoleDTO) -> bool:
        pass
    # END FUNCTION
    
    """
    Modifie le nom du modèle utilisé par l'agent
    
    Args:
        model_name: Nouveau nom de modèle
        
    Returns:
        bool: True si le nom du modèle a été modifié, False sinon
    """
    def set_model_name(self, model_name: str) -> bool:
        pass
    # END FUNCTION
    
    """
    Modifie la température de l'agent
    
    Args:
        temperature: Nouvelle valeur de température
        
    Returns:
        bool: True si la température a été modifiée, False sinon
    """
    def set_temperature(self, temperature: float) -> bool:
        pass
    # END FUNCTION
    
    """
    Vérifie si le nom est valide
    
    Args:
        name: Nom à valider
        
    Returns:
        bool: True si le nom est valide, False sinon
    """
    def validate_name(self, name: str) -> bool:
        pass
    # END FUNCTION
    
    """
    Vérifie si le nom du modèle est valide
    
    Args:
        model_name: Nom du modèle à valider
        
    Returns:
        bool: True si le nom du modèle est valide, False sinon
    """
    def validate_model_name(self, model_name: str) -> bool:
        pass
    # END FUNCTION
    
    """
    Vérifie si la température est valide
    
    Args:
        temperature: Température à valider
        
    Returns:
        bool: True si la température est valide, False sinon
    """
    def validate_temperature(self, temperature: float) -> bool:
        pass
    # END FUNCTION
    
    """
    Convertit l'objet métier Agent en DTO
    
    Returns:
        agentDTO: Le DTO représentant cet agent
    """
    def to_dto(self) -> agentDTO:
        pass
    # END FUNCTION
    
    """
    Crée une instance d'Agent à partir d'un DTO
    
    Args:
        dto: Le DTO à convertir
        
    Returns:
        Agent: Une nouvelle instance d'Agent
    """
    @classmethod
    def from_dto(cls, dto: agentDTO) -> 'Agent':
        pass
    # END FUNCTION
    
    """
    Vérifie si l'agent utilise un modèle spécifique
    
    Args:
        model_name: Nom du modèle à vérifier
        
    Returns:
        bool: True si l'agent utilise ce modèle, False sinon
    """
    def uses_model(self, model_name: str) -> bool:
        pass
    # END FUNCTION
    
    """
    Retourne une représentation de l'agent sous forme de chaîne de caractères
    
    Returns:
        str: Représentation textuelle de l'agent
    """
    def __str__(self) -> str:
        pass
    # END FUNCTION
    
    """
    Compare deux agents pour déterminer s'ils sont égaux
    
    Args:
        other: Autre objet à comparer
        
    Returns:
        bool: True si les agents sont égaux, False sinon
    """
    def __eq__(self, other: object) -> bool:
        pass
    # END FUNCTION