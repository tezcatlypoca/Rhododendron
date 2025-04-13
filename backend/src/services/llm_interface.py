from typing import List, Dict, Any, Optional
import os
from ctransformers import AutoModelForCausalLM
from ..models.domain.conversation import Message, MessageRole

class LLMInterface:
    _instance = None
    _model = None
    _conversation_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInterface, cls).__new__(cls)
            cls._instance.model_name = "codellama-7b-instruct-q4_0"
            print(f"Interface LLM initialisée avec le modèle {cls._instance.model_name}")
            
            # Chargement du modèle
            if cls._instance._model is None:
                # Utilisation du modèle depuis Hugging Face
                model_path = "TheBloke/CodeLlama-7B-Instruct-GGUF"
                model_file = "codellama-7b-instruct.Q4_K_M.gguf"
                
                print(f"Chargement du modèle depuis Hugging Face : {model_path}")
                cls._instance._model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    model_file=model_file,
                    model_type="llama",
                    gpu_layers=0,  # Utilisation du CPU uniquement
                    threads=4,  # Nombre de threads pour l'inférence
                    context_length=2048  # Taille du contexte
                )
                print("Modèle chargé avec succès")
        return cls._instance

    def __init__(self):
        # L'initialisation est maintenant dans __new__
        pass

    @property
    def conversation_service(self):
        if self._conversation_service is None:
            from ..services.conversation_service import ConversationService
            self._conversation_service = ConversationService()
        return self._conversation_service

    def generate_response(self, prompt: str, context: Dict[str, Any], conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Génère une réponse à partir d'un prompt et d'un contexte en utilisant le modèle local.
        
        Args:
            prompt: Le prompt de l'utilisateur
            context: Le contexte de l'agent (rôle, modèle, etc.)
            conversation_history: L'historique de la conversation
            
        Returns:
            La réponse générée par le modèle
        """
        # Construction du prompt complet
        full_prompt = self._build_prompt(prompt, context, conversation_history)
        print(f"Prompt complet : {full_prompt}")
        
        try:
            # Génération de la réponse
            response = self._model(
                full_prompt,
                max_new_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                stop=["Utilisateur:", "\n\n"]
            )
            
            print(f"Réponse générée : {response[:100]}...")
            return response
            
        except Exception as e:
            print(f"Erreur lors de la génération de la réponse : {str(e)}")
            raise

    def _build_prompt(self, prompt: str, context: Dict[str, Any], conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Construit le prompt complet en incluant le contexte et l'historique.
        
        Args:
            prompt: Le prompt de l'utilisateur
            context: Le contexte de l'agent
            conversation_history: L'historique de la conversation
            
        Returns:
            Le prompt complet
        """
        # Construction du prompt système
        role = context.get("role", "assistant")
        system_prompt = f"Tu es un {role}. Réponds de manière professionnelle et précise."
        
        # Ajouter l'historique de la conversation si disponible
        conversation_text = ""
        if conversation_history:
            conversation_text = "\nHistorique de la conversation :\n"
            for message in conversation_history:
                role_prefix = "Utilisateur" if message["role"] == MessageRole.USER else "Assistant"
                conversation_text += f"{role_prefix}: {message['content']}\n"
        
        # Construction du prompt final
        return f"{system_prompt}{conversation_text}\nUtilisateur: {prompt}\nAssistant:" 