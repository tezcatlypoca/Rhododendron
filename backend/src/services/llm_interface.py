"""
Interface LLM utilisant llama.cpp avec le backend DirectML pour les GPU AMD.
Ce module permet d'exécuter des modèles GGUF sur des GPU AMD.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import ctypes
from ..models.domain.conversation import Message, MessageRole

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemin vers les DLL compilées localement
LOCAL_LLAMA_PATH = Path("F:/ToutPleinDeTrucs/Dev/Rhododendron/dependencies/llama.cpp/build/bin/Release")

class LLMInterface:
    """
    Interface pour exécuter des modèles LLM sur GPU AMD via DirectML.
    
    Cette classe gère :
    - Le chargement des modèles GGUF
    - La configuration du backend DirectML
    - L'inférence sur GPU
    - La gestion des paramètres d'inférence
    """
    
    _instance = None
    _model = None
    _conversation_service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInterface, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialise l'interface LLM avec les paramètres par défaut."""
        try:
            # Ajouter le chemin des DLL à la variable d'environnement PATH
            if LOCAL_LLAMA_PATH.exists():
                dll_path = str(LOCAL_LLAMA_PATH)
                os.environ["PATH"] = dll_path + os.pathsep + os.environ["PATH"]
                logger.info(f"Chemin vers llama.cpp configuré : {dll_path}")
                
                # Vérifier l'existence des DLLs
                llama_dll_path = str(LOCAL_LLAMA_PATH / "llama.dll")
                ggml_dll_path = str(LOCAL_LLAMA_PATH / "ggml.dll")
                
                if not os.path.exists(llama_dll_path):
                    raise RuntimeError(f"llama.dll non trouvé à {llama_dll_path}")
                if not os.path.exists(ggml_dll_path):
                    raise RuntimeError(f"ggml.dll non trouvé à {ggml_dll_path}")
                
                logger.info(f"llama.dll trouvé à {llama_dll_path}")
                logger.info(f"ggml.dll trouvé à {ggml_dll_path}")
                
                # Charger les DLL compilées
                try:
                    # Charger d'abord ggml.dll
                    logger.info("Chargement de ggml.dll...")
                    self.ggml_dll = ctypes.WinDLL(ggml_dll_path)
                    logger.info("ggml.dll chargé avec succès")
                    
                    # Puis llama.dll
                    logger.info("Chargement de llama.dll...")
                    self.llama_dll = ctypes.WinDLL(llama_dll_path)
                    logger.info("llama.dll chargé avec succès")
                    
                    # Vérifier que les fonctions existent
                    required_functions = [
                        'llama_token_eos',
                        'llama_token_bos',
                        'llama_free',
                        'llama_tokenize',
                        'llama_eval',
                        'llama_sample_top_p',
                        'llama_token_to_str',
                        'llama_model_default_params',
                        'llama_model_load_from_file',
                        'llama_context_default_params',
                        'llama_new_context_with_model'
                    ]
                    
                    for func_name in required_functions:
                        if not hasattr(self.llama_dll, func_name):
                            raise RuntimeError(f"Fonction {func_name} non trouvée dans llama.dll")
                    
                    logger.info("Toutes les fonctions requises sont présentes")
                    
                    # Définir les fonctions C de base
                    logger.info("Configuration des fonctions C...")
                    self.llama_dll.llama_token_eos.argtypes = []
                    self.llama_dll.llama_token_eos.restype = ctypes.c_int
                    
                    self.llama_dll.llama_token_bos.argtypes = []
                    self.llama_dll.llama_token_bos.restype = ctypes.c_int
                    
                    self.llama_dll.llama_free.argtypes = [ctypes.c_void_p]
                    self.llama_dll.llama_free.restype = None
                    
                    # Définir les fonctions pour la tokenization et l'évaluation
                    self.llama_dll.llama_tokenize.argtypes = [
                        ctypes.c_void_p,  # ctx
                        ctypes.c_char_p,  # text
                        ctypes.POINTER(ctypes.c_int),  # tokens
                        ctypes.c_int,     # n_max_tokens
                        ctypes.c_bool     # add_bos
                    ]
                    self.llama_dll.llama_tokenize.restype = ctypes.c_int
                    
                    self.llama_dll.llama_eval.argtypes = [
                        ctypes.c_void_p,  # ctx
                        ctypes.POINTER(ctypes.c_int),  # tokens
                        ctypes.c_int,     # n_tokens
                        ctypes.c_int      # n_past
                    ]
                    self.llama_dll.llama_eval.restype = ctypes.c_int
                    
                    self.llama_dll.llama_sample_top_p.argtypes = [
                        ctypes.c_void_p,  # ctx
                        ctypes.POINTER(ctypes.c_int),  # last_n_tokens
                        ctypes.c_int,     # last_n_tokens_size
                        ctypes.c_float,   # top_p
                        ctypes.c_float,   # temperature
                        ctypes.c_int      # n_threads
                    ]
                    self.llama_dll.llama_sample_top_p.restype = ctypes.c_int
                    
                    self.llama_dll.llama_token_to_str.argtypes = [
                        ctypes.c_void_p,  # ctx
                        ctypes.c_int      # token
                    ]
                    self.llama_dll.llama_token_to_str.restype = ctypes.c_char_p
                    
                    logger.info("Configuration des fonctions C terminée")
                    
                except Exception as e:
                    logger.error(f"Erreur lors du chargement des DLL : {str(e)}")
                    logger.error(f"Type d'erreur : {type(e).__name__}")
                    logger.error(f"Message d'erreur : {str(e)}")
                    raise RuntimeError(f"Impossible de charger les DLL compilées : {str(e)}")
            else:
                logger.warning("Version compilée de llama.cpp non trouvée")
                raise RuntimeError("Version compilée de llama.cpp non trouvée")
            
            # Configuration DirectML
            self._setup_directml()
            
            # Paramètres d'inférence par défaut
            self.default_params = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1000,
                "stop": ["Utilisateur:", "\n\n"],
                "repeat_penalty": 1.1
            }
            
            logger.info("Interface LLM initialisée")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation : {str(e)}")
            raise
    
    def _setup_directml(self):
        """Configure l'environnement pour utiliser DirectML."""
        try:
            # Configurer les variables d'environnement pour DirectML
            os.environ["LLAMA_DML"] = "1"
            os.environ["DML_DEBUG_LAYER"] = "0"  # Désactiver le mode debug
            os.environ["DML_GPU_LAYERS"] = "32"  # Forcer l'utilisation du GPU
            os.environ["DML_MAIN_GPU"] = "0"     # Utiliser le premier GPU
            os.environ["LLAMA_DML_OFFLOAD"] = "1"  # Forcer l'offload sur GPU
            os.environ["DML_GPU_DEVICE"] = "0"    # Utiliser le premier GPU AMD
            
            # Vérifier si DirectML est disponible
            try:
                dml = ctypes.WinDLL("DirectML.dll")
                logger.info("DirectML est disponible")
            except Exception as e:
                logger.error(f"DirectML n'est pas disponible : {str(e)}")
                raise RuntimeError("DirectML n'est pas disponible sur ce système")
            
            logger.info("Configuration DirectML terminée")
            
        except Exception as e:
            logger.error(f"Erreur lors de la configuration de DirectML : {str(e)}")
            raise
    
    def load_model(self, model_path: Optional[Union[str, Path]] = None) -> None:
        """
        Charge un modèle GGUF.
        
        Args:
            model_path: Chemin vers le fichier modèle. Si None, utilise le chemin par défaut.
        """
        try:
            if model_path is None:
                model_path = Path("F:/ToutPleinDeTrucs/Dev/Rhododendron/backend/llm_models/codellama-7b-instruct-q4_0.gguf")
            else:
                model_path = Path(model_path)
            
            if not model_path.exists():
                raise FileNotFoundError(f"Le modèle n'existe pas à l'emplacement : {model_path}")
            
            logger.info(f"Chargement du modèle depuis {model_path}")
            start_time = time.time()
            
            # Définir les types des fonctions
            self.llama_dll.llama_model_default_params.argtypes = []
            self.llama_dll.llama_model_default_params.restype = ctypes.c_void_p
            
            self.llama_dll.llama_model_load_from_file.argtypes = [
                ctypes.c_char_p,  # model_path
                ctypes.c_void_p   # params
            ]
            self.llama_dll.llama_model_load_from_file.restype = ctypes.c_void_p
            
            self.llama_dll.llama_context_default_params.argtypes = []
            self.llama_dll.llama_context_default_params.restype = ctypes.c_void_p
            
            self.llama_dll.llama_new_context_with_model.argtypes = [
                ctypes.c_void_p,  # model
                ctypes.c_void_p   # params
            ]
            self.llama_dll.llama_new_context_with_model.restype = ctypes.c_void_p
            
            # Charger le modèle
            model_params = self.llama_dll.llama_model_default_params()
            self._model = self.llama_dll.llama_model_load_from_file(
                str(model_path).encode('utf-8'),
                model_params
            )
            
            if not self._model:
                raise RuntimeError("Impossible de charger le modèle")
            
            # Créer le contexte
            ctx_params = self.llama_dll.llama_context_default_params()
            self._ctx = self.llama_dll.llama_new_context_with_model(self._model, ctx_params)
            
            if not self._ctx:
                raise RuntimeError("Impossible de créer le contexte")
            
            load_time = time.time() - start_time
            logger.info(f"Modèle chargé avec succès en {load_time:.2f} secondes")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
            raise
    
    def generate_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """
        Génère une réponse à partir d'un prompt.
        """
        try:
            logger.info("Début de la génération de réponse")
            
            if not self._ctx:
                raise RuntimeError("Le modèle n'est pas chargé")
            
            # Construire le prompt complet
            full_prompt = self._build_prompt(prompt, context, conversation_history)
            logger.info(f"Prompt complet : {full_prompt[:100]}...")
            
            # Définir les paramètres de génération
            params = kwargs.get("params", self.default_params)
            max_tokens = params.get("max_tokens", 1000)
            temperature = params.get("temperature", 0.7)
            top_p = params.get("top_p", 0.9)
            stop = params.get("stop", ["Utilisateur:", "\n\n"])
            
            logger.info(f"Paramètres de génération : max_tokens={max_tokens}, temperature={temperature}, top_p={top_p}")
            
            # Convertir le prompt en tokens
            logger.info("Tokenization du prompt")
            n_tokens = 1000
            tokens = (ctypes.c_int * n_tokens)()
            n_tokens = self.llama_dll.llama_tokenize(
                self._ctx,
                full_prompt.encode('utf-8'),
                tokens,
                n_tokens,
                True
            )
            
            if n_tokens <= 0:
                raise RuntimeError("Impossible de tokenizer le prompt")
            
            logger.info(f"Nombre de tokens : {n_tokens}")
            
            # Générer la réponse
            logger.info("Début de la génération token par token")
            response_tokens = []
            for i in range(max_tokens):
                try:
                    # Évaluer les tokens actuels
                    result = self.llama_dll.llama_eval(
                        self._ctx,
                        tokens,
                        n_tokens,
                        0  # n_past = 0 pour commencer
                    )
                    
                    if result != 0:
                        raise RuntimeError(f"Erreur lors de l'évaluation : {result}")
                    
                    # Obtenir le prochain token
                    next_token = self.llama_dll.llama_sample_top_p(
                        self._ctx,
                        tokens,
                        n_tokens,
                        top_p,
                        temperature,
                        8  # n_threads
                    )
                    
                    # Vérifier si on a atteint un token de fin
                    if next_token == self.llama_dll.llama_token_eos():
                        logger.info("Token de fin détecté")
                        break
                    
                    response_tokens.append(next_token)
                    
                    # Mettre à jour les tokens pour la prochaine itération
                    tokens = (ctypes.c_int * n_tokens)(*tokens[1:], next_token)
                    
                    # Vérifier les conditions d'arrêt
                    if i % 10 == 0:  # Tous les 10 tokens
                        current_text = self._tokens_to_text(response_tokens)
                        if any(stop_token in current_text for stop_token in stop):
                            logger.info("Condition d'arrêt détectée")
                            break
                
                except Exception as e:
                    logger.error(f"Erreur lors de la génération du token {i}: {str(e)}")
                    raise
            
            # Convertir les tokens en texte
            logger.info("Conversion des tokens en texte")
            response = self._tokens_to_text(response_tokens)
            
            logger.info(f"Réponse générée : {response[:100]}...")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération : {str(e)}")
            raise
    
    def _build_prompt(
        self,
        prompt: str,
        context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Construit le prompt complet.
        """
        # Construction du prompt système
        role = context.get("role", "assistant")
        system_prompt = f"Tu es un {role}. Réponds de manière professionnelle et précise."
        
        # Ajouter l'historique de la conversation
        conversation_text = ""
        if conversation_history:
            conversation_text = "\nHistorique de la conversation :\n"
            for message in conversation_history:
                role_prefix = "Utilisateur" if message["role"] == MessageRole.USER else "Assistant"
                conversation_text += f"{role_prefix}: {message['content']}\n"
        
        # Construction du prompt final
        return f"{system_prompt}\n{conversation_text}\nUtilisateur: {prompt}\nAssistant:"
    
    def _tokens_to_text(self, tokens: List[int]) -> str:
        """Convertit une liste de tokens en texte."""
        try:
            text = ""
            for token in tokens:
                token_str = self.llama_dll.llama_token_to_str(self._ctx, token)
                if token_str:
                    text += token_str.decode('utf-8', errors='ignore')
            return text
        except Exception as e:
            logger.error(f"Erreur lors de la conversion des tokens en texte : {str(e)}")
            raise
    
    @property
    def conversation_service(self):
        if self._conversation_service is None:
            from ..services.conversation_service import ConversationService
            self._conversation_service = ConversationService()
        return self._conversation_service