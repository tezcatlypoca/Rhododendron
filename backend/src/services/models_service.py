# scripts/download_model.py
from transformers import AutoModelForCausalLM
import os

def download_model():
    model_path = "F:/ToutPleinDeTrucs/Dev/Rhododendron/backend/llm_models"
    os.makedirs(model_path, exist_ok=True)
    
    # Télécharger le modèle
    model = AutoModelForCausalLM.from_pretrained(
        "codellama/CodeLlama-7b-Instruct-hf",
        export=True,
        format="onnx"
    )
    
    # Sauvegarder le modèle
    model.save_pretrained(model_path)

if __name__ == "__main__":
    download_model()