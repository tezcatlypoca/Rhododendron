from typing import List, Dict, Any, Optional
import os
import warnings
from ctransformers import AutoModelForCausalLM
from ..models.domain.conversation import Message, MessageRole

# Désactiver les avertissements spécifiques
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")
warnings.filterwarnings("ignore", category=FutureWarning, module="onnxscript")

class LLMInterface:
    _instance = None
    _model = None
    _conversation_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInterface, cls).__new__(cls)
            # Chemin vers le modèle local
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_dir, "llm_models", "codellama-7b-instruct-q4_0.gguf")
            
            # Vérification de l'existence du fichier
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Le modèle n'a pas été trouvé à l'emplacement : {model_path}")
            
            cls._instance.model_path = model_path
            print(f"Interface LLM initialisée avec le modèle local : {cls._instance.model_path}")
        return cls._instance

    def __init__(self):
        # L'initialisation est maintenant dans __new__
        pass

    def _load_model(self):
        """Charge le modèle uniquement si nécessaire"""
        if self._model is None:
            try:
                print(f"Chargement du modèle depuis le chemin local : {self.model_path}")
                
                # Vérification de l'existence du fichier
                if not os.path.exists(self.model_path):
                    raise FileNotFoundError(f"Le modèle n'a pas été trouvé à l'emplacement : {self.model_path}")
                
                # Chargement du modèle avec optimisations CPU
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    model_type="llama",
                    gpu_layers=0,  # Utilisation du CPU uniquement
                    threads=4,  # Nombre de threads pour l'inférence
                    context_length=2048  # Taille du contexte
                )
                
                print("Modèle chargé avec succès")
            except Exception as e:
                print(f"Erreur lors du chargement du modèle : {str(e)}")
                raise

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
        # Chargement du modèle si nécessaire
        self._load_model()
        
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