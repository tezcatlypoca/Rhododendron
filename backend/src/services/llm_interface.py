from typing import List, Dict, Any, Optional
import os
import pyopencl as cl
import numpy as np
from ..models.domain.conversation import Message, MessageRole

class LLMInterface:
    _instance = None
    _context = None
    _queue = None
    _program = None
    _conversation_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInterface, cls).__new__(cls)
            print("Initialisation de l'interface LLM avec OpenCL")

            # Initialisation de la plateforme et du GPU
            platforms = cl.get_platforms()
            if not platforms:
                raise RuntimeError("Aucune plateforme OpenCL détectée.")
            
            # Sélectionner la première plateforme et le premier GPU
            platform = platforms[0]
            devices = platform.get_devices(device_type=cl.device_type.GPU)
            if not devices:
                raise RuntimeError("Aucun GPU détecté sur la plateforme OpenCL.")
            
            device = devices[0]
            print(f"Utilisation du GPU : {device.name}")

            # Créer le contexte et la file d'attente
            cls._context = cl.Context([device])
            cls._queue = cl.CommandQueue(cls._context)

            # Charger le programme OpenCL (kernel)
            kernel_code = """
            __kernel void add_vectors(__global const float *a, __global const float *b, __global float *result) {
                int gid = get_global_id(0);
                result[gid] = a[gid] + b[gid];
            }
            """
            cls._program = cl.Program(cls._context, kernel_code).build()
            print("Programme OpenCL chargé avec succès.")
        
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

    """ def add_vectors(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        Exemple de calcul sur GPU : addition de deux vecteurs.
        
        Args:
            a: Premier vecteur (numpy array).
            b: Deuxième vecteur (numpy array).
        
        Returns:
            Le résultat de l'addition (numpy array).

        if a.shape != b.shape:
            raise ValueError("Les vecteurs doivent avoir la même taille.")
        
        # Préparer les buffers OpenCL
        mf = cl.mem_flags
        a_buf = cl.Buffer(self._context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
        b_buf = cl.Buffer(self._context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b)
        result_buf = cl.Buffer(self._context, mf.WRITE_ONLY, a.nbytes)

        # Exécuter le kernel
        self._program.add_vectors(self._queue, a.shape, None, a_buf, b_buf, result_buf)

        # Récupérer les résultats
        result = np.empty_like(a)
        cl.enqueue_copy(self._queue, result, result_buf)
        return result """

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
) 

def print_model_metadata(model_file_path):

    #Affiche les métadonnées du modèle, y compris la taille totale, le nombre de couches, et la taille des couches.

    from llama_cpp import Llama

    print(f"Chargement des métadonnées du modèle depuis : {model_file_path}")
    model = Llama(model_path=model_file_path, n_gpu_layers=0, use_mmap=True)  # Charger uniquement les métadonnées

    # Afficher les métadonnées importantes
    print("=== Métadonnées du modèle ===")
    print(f"Taille totale du modèle : {model.metadata['general.file_size']} octets")
    print(f"Nombre de couches : {model.metadata['llama.block_count']}")
    print(f"Taille des embeddings : {model.metadata['llama.embedding_length']}")
    print(f"Taille du feed-forward : {model.metadata['llama.feed_forward_length']}")
    print(f"Nombre de têtes d'attention : {model.metadata['llama.attention.head_count']}")
    print(f"Nombre de têtes clés/valeurs : {model.metadata['llama.attention.head_count_kv']}")
    print("=============================")

"""