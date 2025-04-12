from typing import Dict, Any, Optional
import os
import json
import subprocess
import tempfile
import sys

class LLMInterface:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.model_name = "codellama:7b-instruct-q4_0"
        print(f"Interface LLM initialisée avec le modèle {self.model_name}")
        
        # Configuration pour utiliser le GPU AMD
        os.environ["OLLAMA_GPU_LAYER"] = "rocm"  # Pour AMD ROCm
        os.environ["OLLAMA_GPU_DEVICE"] = "0"    # Premier GPU
        
        # Vérification que le modèle est installé
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, encoding='utf-8')
            if self.model_name not in result.stdout:
                print(f"Le modèle {self.model_name} n'est pas installé. Tentative d'installation...")
                subprocess.run(['ollama', 'pull', self.model_name], check=True, encoding='utf-8')
                print("Modèle installé avec succès")
            else:
                print(f"Modèle {self.model_name} trouvé et prêt à être utilisé")
                
            # Vérification de l'utilisation du GPU
            gpu_info = subprocess.run(['ollama', 'info'], capture_output=True, text=True, encoding='utf-8')
            print(f"Informations sur le GPU : {gpu_info.stdout}")
            
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la vérification du modèle : {str(e)}")
            raise

    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Génère une réponse à partir d'un prompt et d'un contexte optionnel en utilisant Ollama en local.
        
        Args:
            prompt: Le prompt de l'utilisateur
            context: Dictionnaire contenant le contexte de l'agent (role, etc.)
        
        Returns:
            La réponse générée par le modèle
        """
        # Construction du prompt complet avec le contexte
        full_prompt = self._build_prompt(prompt, context)
        print(f"Prompt complet : {full_prompt}")
        
        try:
            # Exécution de la commande Ollama en local avec le prompt directement
            cmd = ['ollama', 'run', self.model_name]
            print(f"Exécution de la commande : {' '.join(cmd)}")
            
            # Utilisation de Popen pour gérer l'entrée/sortie
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # Envoi du prompt et récupération de la réponse
            stdout, stderr = process.communicate(input=full_prompt)
            
            if process.returncode != 0:
                raise Exception(f"Erreur lors de l'exécution d'Ollama : {stderr}")
            
            response = stdout.strip()
            print(f"Réponse générée : {response[:100]}...")
            return response
            
        except Exception as e:
            print(f"Erreur lors de la génération de la réponse : {str(e)}")
            raise

    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Construit le prompt complet en incluant le contexte.
        """
        if context is None:
            return prompt
            
        role = context.get("role", "assistant")
        system_prompt = f"Tu es un {role}. Réponds de manière professionnelle et précise."
        
        return f"{system_prompt}\n\nUtilisateur: {prompt}\nAssistant:" 