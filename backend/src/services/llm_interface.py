from typing import Dict, Any, Optional
import os
from ctransformers import AutoModelForCausalLM
from ..models.domain.conversation import Message, MessageRole
from ..services.conversation_service import ConversationService

class LLMInterface:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.model_name = "codellama-7b-instruct-q4_0"
        self.conversation_service = ConversationService()
        print(f"Interface LLM initialisée avec le modèle {self.model_name}")
        
        # Chargement du modèle
        if self._model is None:
            # Utilisation du modèle depuis Hugging Face
            model_path = "TheBloke/CodeLlama-7B-Instruct-GGUF"
            model_file = "codellama-7b-instruct.Q4_K_M.gguf"
            
            print(f"Chargement du modèle depuis Hugging Face : {model_path}")
            self._model = AutoModelForCausalLM.from_pretrained(
                model_path,
                model_file=model_file,
                model_type="llama",
                gpu_layers=0,  # Utilisation du CPU uniquement
                threads=4,  # Nombre de threads pour l'inférence
                context_length=2048  # Taille du contexte
            )
            print("Modèle chargé avec succès")

    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None, conversation_id: Optional[str] = None) -> str:
        """
        Génère une réponse à partir d'un prompt et d'un contexte optionnel en utilisant le modèle local.
        
        Args:
            prompt: Le prompt de l'utilisateur
            context: Dictionnaire contenant le contexte de l'agent (role, etc.)
            conversation_id: ID de la conversation en cours (optionnel)
        
        Returns:
            La réponse générée par le modèle
        """
        # Construction du prompt complet avec le contexte
        full_prompt = self._build_prompt(prompt, context, conversation_id)
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

    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None, conversation_id: Optional[str] = None) -> str:
        """
        Construit le prompt complet en incluant le contexte et l'historique de la conversation.
        """
        # Récupération de l'historique de la conversation si disponible
        conversation_history = ""
        if conversation_id:
            conversation = self.conversation_service.get_conversation(conversation_id)
            if conversation:
                # On prend les 5 derniers messages pour le contexte
                last_messages = conversation.get_last_messages(5)
                for msg in last_messages:
                    role_prefix = "Utilisateur" if msg.role == MessageRole.USER else "Assistant"
                    conversation_history += f"{role_prefix}: {msg.content}\n"
        
        # Construction du prompt système
        if context is None:
            system_prompt = "Tu es un assistant IA. Réponds de manière professionnelle et précise."
        else:
            role = context.get("role", "assistant")
            system_prompt = f"Tu es un {role}. Réponds de manière professionnelle et précise."
        
        # Construction du prompt final
        if conversation_history:
            return f"{system_prompt}\n\nHistorique de la conversation :\n{conversation_history}\n\nUtilisateur: {prompt}\nAssistant:"
        else:
            return f"{system_prompt}\n\nUtilisateur: {prompt}\nAssistant:" 