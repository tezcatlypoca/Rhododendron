from typing import List, Dict, Any, Optional
import os
import torch
from llama_cpp import Llama
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
            
            # Configuration pour ROCm
            os.environ["HIP_VISIBLE_DEVICES"] = "0,1"  # Utiliser les deux GPU
            os.environ["HSA_OVERRIDE_GFX_VERSION"] = "9.0.0"  # Pour Vega 64
            
            # Vérification de la disponibilité des GPU
            print("Vérification des GPU...")
            print(f"CUDA disponible: {torch.cuda.is_available()}")
            print(f"Nombre de GPU CUDA: {torch.cuda.device_count()}")
            print(f"Version CUDA: {torch.version.cuda if torch.cuda.is_available() else 'N/A'}")
            print(f"Version ROCm: {torch.version.hip if hasattr(torch.version, 'hip') else 'N/A'}")
            
            # Chargement du modèle
            if cls._instance._model is None:
                # Utilisation du modèle depuis Hugging Face
                model_path = "TheBloke/CodeLlama-7B-Instruct-GGUF"
                model_file = "codellama-7b-instruct.Q4_K_M.gguf"
                
                print(f"Chargement du modèle depuis Hugging Face : {model_path}")
                cls._instance._model = Llama(
                    model_path=model_file,
                    n_gpu_layers=-1,  # Utiliser tous les layers sur GPU
                    n_ctx=4096,
                    n_batch=512,
                    tensor_split=[0.5, 0.5],  # Répartition entre les deux GPUs
                    n_threads=16,  # Nombre de threads pour le CPU
                    # use_mmap=True,  # Utilisation de la mémoire mmap
                    # use_mlock=True  # Verrouillage de la mémoire
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
            # Configuration des paramètres de génération
            generation_config = {
                "max_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9,
                "stop": ["Utilisateur:", "\n\n"],
                "repeat_penalty": 1.1
            }
            
            # Génération de la réponse
            response = self._model(
                full_prompt,
                **generation_config
            )
            
            print(f"Réponse générée : {response['choices'][0]['text'][:100]}...")
            return response['choices'][0]['text']
            
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
        return f"{system_prompt}\n{conversation_text}\nUtilisateur: {prompt}\nAssistant:" 