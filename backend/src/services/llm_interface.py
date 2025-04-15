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
            
            # Définir le chemin absolu vers le fichier modèle
            model_file_path = os.path.expanduser("~/Documents/Rhododendron/backend/models/codellama-7b-instruct.Q4_K_M.gguf.1")
            print(f"Chemin absolu du fichier modèle : {model_file_path}")

            # Vérifier l'existence du fichier
            if not os.path.exists(model_file_path):
                raise FileNotFoundError(f"Modèle non trouvé: {model_file_path}")
            
            print(f"Fichier modèle trouvé à: {model_file_path}")
            
            # Chargement du modèle avec utilisation des GPU
            cls._instance._model = Llama(
                model_path=model_file_path,
                n_gpu_layers=40,  # Nombre de couches à charger sur le GPU
                n_ctx=4096,  # Taille du contexte
                n_threads=16,  # Nombre de threads pour le CPU
                tensor_split=[0.5, 0.5],  # Répartition des tenseurs entre deux GPU (si disponibles)
                use_mmap=True,  # Utilisation de la mémoire mmap pour optimiser le chargement
                use_mlock=True  # Verrouillage de la mémoire pour éviter le swap
            )
            print("Modèle chargé avec succès via llama_cpp")
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
    
""" import subprocess

def get_gpu_memory():
    # Utiliser rocm-smi pour récupérer la mémoire disponible sur chaque GPU
    result = subprocess.run(["rocm-smi", "--showmeminfo", "vram"], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    memory_available = []
    for line in lines:
        if "Used" in line:
            used = int(line.split(":")[1].strip().split(" ")[0])
        if "Total" in line:
            total = int(line.split(":")[1].strip().split(" ")[0])
            memory_available.append(total - used)
    return memory_available

# Calculer n_gpu_layers en fonction de la mémoire disponible
gpu_memory = get_gpu_memory()
n_gpu_layers = min((min(gpu_memory) // 200) * len(gpu_memory), 40)  # Estimation : 200 Mo par couche
tensor_split = [1 / len(gpu_memory)] * len(gpu_memory)

cls._instance._model = Llama(
    model_path=model_file_path,
    n_gpu_layers=n_gpu_layers,
    tensor_split=tensor_split,
    n_ctx=4096,
    n_threads=16,
    use_mmap=True,
    use_mlock=True
) """