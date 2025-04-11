from typing import Dict, Any, Optional
import requests
import json

class LLMInterface:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.base_url = "http://localhost:11434"  # Suppression de /api car Ollama l'ajoute automatiquement
        self.model_name = "codellama"  # Nom du modèle dans Ollama
        print(f"Interface LLM initialisée avec le modèle {self.model_name}")

    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Génère une réponse à partir d'un prompt et d'un contexte optionnel en utilisant l'API Ollama.
        
        Args:
            prompt: Le prompt de l'utilisateur
            context: Dictionnaire contenant le contexte de l'agent (role, etc.)
        
        Returns:
            La réponse générée par le modèle
        """
        # Construction du prompt complet avec le contexte
        full_prompt = self._build_prompt(prompt, context)
        print(f"Prompt complet : {full_prompt}")
        
        # Préparation de la requête
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            print("Envoi de la requête à Ollama...")
            # Envoi de la requête à l'API Ollama
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            
            # Extraction de la réponse
            result = response.json()
            print(f"Réponse reçue de Ollama")
            return result["response"].strip()
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la communication avec Ollama: {str(e)}")
            raise Exception(f"Erreur lors de la communication avec Ollama: {str(e)}")

    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Construit le prompt complet en incluant le contexte.
        """
        if context is None:
            return prompt
            
        role = context.get("role", "assistant")
        system_prompt = f"Tu es un {role}. Réponds de manière professionnelle et précise."
        
        return f"{system_prompt}\n\nUtilisateur: {prompt}\nAssistant:" 