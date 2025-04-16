"""
Interface LLM utilisant llama.cpp avec le backend DirectML pour les GPU AMD.
Ce module permet d'exécuter des modèles GGUF sur des GPU AMD.
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Union
from ..models.domain.conversation import Message, MessageRole

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemin vers les exécutables compilés localement
LOCAL_LLAMA_PATH = Path("F:/ToutPleinDeTrucs/Dev/Rhododendron/dependencies/llama.cpp/build/bin/Release")

class LLMInterface:
    """
    Interface pour exécuter des modèles LLM sur GPU AMD via DirectML.
    """
    
    _instance = None
    _model_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInterface, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialise l'interface LLM."""
        try:
            if not LOCAL_LLAMA_PATH.exists():
                raise RuntimeError(f"Le répertoire des exécutables n'existe pas: {LOCAL_LLAMA_PATH}")
            
            # Vérifier la présence de llama.dll
            llama_dll_path = LOCAL_LLAMA_PATH / "llama.dll"
            if not llama_dll_path.exists():
                raise RuntimeError(f"llama.dll non trouvé à {llama_dll_path}")
            
            logger.info(f"llama.dll trouvé à {llama_dll_path}")
            
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
            if not self._model_path:
                raise RuntimeError("Le modèle n'est pas chargé")
            
            # Construire le prompt complet avec le format instruct
            role = context.get("role", "assistant")
            system_prompt = f"Tu es un {role} professionnel et compétent. Tu dois répondre de manière claire et concise."
            full_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"
            
            # Construire la commande avec llama-cli.exe
            cmd = [
                str(LOCAL_LLAMA_PATH / "llama-cli.exe"),
                "--model", str(self._model_path),
                "--prompt", full_prompt,
                "--n-predict", "256",
                "--temp", "0.7",
                "--top-p", "0.9",
                "--ctx-size", "1024",
                "--repeat-penalty", "1.1",
                "--mlock"
            ]
            
            # Afficher la commande pour le débogage
            logger.info("Commande complète:")
            logger.info(f"Exécutable: {cmd[0]}")
            logger.info(f"Modèle: {cmd[2]}")
            logger.info(f"Arguments: {' '.join(cmd[5:])}")
            
            # Exécuter la commande avec un timeout plus long
            try:
                start_time = time.time()
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='latin-1',
                    timeout=60
                )
                
                # Calculer le temps d'exécution
                execution_time = time.time() - start_time
                logger.info(f"Temps d'exécution: {execution_time:.2f} secondes")
                
                # Afficher la sortie d'erreur pour le débogage
                if result.stderr:
                    logger.error(f"Erreur: {result.stderr}")
                
                # Convertir la sortie en UTF-8
                response = result.stdout.strip()
                try:
                    response = response.encode('latin-1').decode('utf-8')
                except UnicodeError:
                    pass
                
                # Nettoyer la réponse pour ne garder que la partie après [/INST]
                if "[/INST]" in response:
                    response = response.split("[/INST]")[1].strip()
                
                logger.info(f"Réponse générée: {response[:100]}...")
                return response
                
            except subprocess.TimeoutExpired:
                raise RuntimeError("La génération a dépassé le timeout de 1 minute")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {str(e)}")
            raise