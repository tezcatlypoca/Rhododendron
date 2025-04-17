"""
Interface LLM utilisant llama.cpp avec le backend DirectML pour les GPU AMD.
Ce module permet d'exécuter des modèles GGUF sur des GPU AMD.
"""

import os
import sys
import time
import logging
import ctypes
from pathlib import Path
from typing import Dict, Any, Optional, Union
from ..models.domain.conversation import Message, MessageRole

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemin vers les DLLs compilées localement
LOCAL_LLAMA_PATH = Path("F:/ToutPleinDeTrucs/Dev/Rhododendron/dependencies/llama.cpp/build/bin/Release")

# Définition des types C
class llama_context(ctypes.Structure):
    pass

class llama_model(ctypes.Structure):
    pass

class llama_token(ctypes.c_int):
    pass

class LLMInterface:
    """
    Interface pour exécuter des modèles LLM sur GPU AMD via DirectML.
    """
    
    _instance = None
    _model_path = None
    _llama_lib = None
    _model = None
    _ctx = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInterface, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialise l'interface LLM."""
        try:
            if not LOCAL_LLAMA_PATH.exists():
                raise RuntimeError(f"Le répertoire des DLLs n'existe pas: {LOCAL_LLAMA_PATH}")
            
            # Vérifier la présence de llama.dll
            llama_dll_path = LOCAL_LLAMA_PATH / "llama.dll"
            if not llama_dll_path.exists():
                raise RuntimeError(f"llama.dll non trouvé à {llama_dll_path}")
            
            # Charger la DLL
            self._llama_lib = ctypes.CDLL(str(llama_dll_path))
            logger.info(f"llama.dll chargée depuis {llama_dll_path}")
            
            # Définir les prototypes des fonctions de base
            self._llama_lib.llama_load_model_from_file.restype = ctypes.POINTER(llama_model)
            self._llama_lib.llama_load_model_from_file.argtypes = [
                ctypes.c_char_p,  # model_path
                ctypes.c_int,     # n_ctx
                ctypes.c_int,     # n_gpu_layers
            ]
            
            self._llama_lib.llama_new_context_with_model.restype = ctypes.POINTER(llama_context)
            self._llama_lib.llama_new_context_with_model.argtypes = [
                ctypes.POINTER(llama_model),  # model
                ctypes.c_int,                 # n_ctx
            ]
            
            self._llama_lib.llama_tokenize.restype = ctypes.c_int
            self._llama_lib.llama_tokenize.argtypes = [
                ctypes.POINTER(llama_model),  # model
                ctypes.c_char_p,              # text
                ctypes.c_int,                 # text_len
                ctypes.POINTER(llama_token),  # tokens
                ctypes.c_int,                 # n_max_tokens
                ctypes.c_bool,                # add_bos
            ]
            
            self._llama_lib.llama_eval_sequence.restype = ctypes.c_int
            self._llama_lib.llama_eval_sequence.argtypes = [
                ctypes.POINTER(llama_context),  # ctx
                ctypes.POINTER(llama_token),    # tokens
                ctypes.c_int,                   # n_tokens
                ctypes.c_int,                   # n_past
                ctypes.c_int,                   # n_threads
            ]
            
            self._llama_lib.llama_sample_token.restype = llama_token
            self._llama_lib.llama_sample_token.argtypes = [
                ctypes.POINTER(llama_context),  # ctx
            ]
            
            self._llama_lib.llama_token_to_str.restype = ctypes.c_char_p
            self._llama_lib.llama_token_to_str.argtypes = [
                ctypes.POINTER(llama_model),  # model
                llama_token,                  # token
            ]
            
            # Configuration DirectML
            self._setup_directml()
            
            # Initialiser _model_path à None
            self._model_path = None
            
            logger.info("Interface LLM initialisée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {str(e)}")
            raise
    
    def _setup_directml(self):
        """Configure l'environnement pour utiliser DirectML."""
        try:
            # Configuration DirectML pour GPU AMD
            os.environ["LLAMA_DML"] = "1"
            os.environ["DML_DEBUG_LAYER"] = "1"
            os.environ["DML_GPU_LAYERS"] = "100"
            os.environ["DML_MAIN_GPU"] = "0"
            os.environ["LLAMA_DML_OFFLOAD"] = "1"
            os.environ["DML_GPU_DEVICE"] = "0"
            
            # Vérifier la configuration
            logger.info("Configuration DirectML:")
            for key, value in os.environ.items():
                if key.startswith("DML_") or key.startswith("LLAMA_"):
                    logger.info(f"{key}: {value}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la configuration de DirectML: {str(e)}")
            raise
    
    def load_model(self, model_path: Optional[Union[str, Path]] = None) -> None:
        """Charge un modèle GGUF."""
        try:
            if model_path is None:
                model_path = Path("F:/ToutPleinDeTrucs/Dev/Rhododendron/backend/llm_models/codellama-7b-instruct-q4_0.gguf")
            else:
                model_path = Path(model_path)
            
            if not model_path.exists():
                raise FileNotFoundError(f"Le modèle n'existe pas à l'emplacement: {model_path}")
            
            self._model_path = model_path
            
            # Charger le modèle
            n_ctx = 2048  # Taille du contexte
            n_gpu_layers = 100  # Nombre de couches sur GPU
            
            self._model = self._llama_lib.llama_load_model_from_file(
                str(model_path).encode('utf-8'),
                n_ctx,
                n_gpu_layers
            )
            
            if not self._model:
                raise RuntimeError("Échec du chargement du modèle")
            
            # Créer le contexte
            self._ctx = self._llama_lib.llama_new_context_with_model(self._model, n_ctx)
            
            if not self._ctx:
                raise RuntimeError("Échec de la création du contexte")
            
            logger.info(f"Modèle chargé depuis {model_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {str(e)}")
            raise
    
    def generate_response(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Génère une réponse à partir d'un prompt.
        """
        try:
            if not self._model or not self._ctx:
                raise RuntimeError("Le modèle n'est pas chargé")
            
            # Construire le prompt complet avec le format instruct
            role = context.get("role", "assistant")
            system_prompt = f"Tu es un {role} professionnel et compétent. Tu dois répondre de manière claire et concise."
            full_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"
            
            # Convertir le prompt en tokens
            prompt_bytes = full_prompt.encode('utf-8')
            max_tokens = 256
            tokens = (llama_token * max_tokens)()
            n_tokens = self._llama_lib.llama_tokenize(
                self._model,
                prompt_bytes,
                len(prompt_bytes),
                tokens,
                max_tokens,
                True
            )
            
            if n_tokens <= 0:
                raise RuntimeError("Échec de la tokenisation")
            
            # Générer la réponse
            response_tokens = []
            start_time = time.time()
            
            for i in range(n_tokens, max_tokens):
                # Évaluer les tokens
                if self._llama_lib.llama_eval_sequence(self._ctx, tokens, i, 0, 4) != 0:
                    raise RuntimeError("Échec de l'évaluation")
                
                # Échantillonner le prochain token
                token = self._llama_lib.llama_sample_token(self._ctx)
                if token == 2:  # Token EOS
                    break
                
                response_tokens.append(token)
                tokens[i] = token
            
            # Calculer le temps d'exécution
            execution_time = time.time() - start_time
            logger.info(f"Temps d'exécution: {execution_time:.2f} secondes")
            
            # Convertir les tokens en texte
            response_parts = []
            for token in response_tokens:
                token_str = self._llama_lib.llama_token_to_str(self._model, token)
                if token_str:
                    response_parts.append(token_str.decode('utf-8'))
            
            response_str = ''.join(response_parts)
            
            # Nettoyer la réponse pour ne garder que la partie après [/INST]
            if "[/INST]" in response_str:
                response_str = response_str.split("[/INST]")[1].strip()
            
            logger.info(f"Réponse générée: {response_str[:100]}...")
            return response_str
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {str(e)}")
            raise