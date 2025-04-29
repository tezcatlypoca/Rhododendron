import requests
import os

def download_file(url, filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192
    
    with open(filename, 'wb') as f:
        for data in response.iter_content(block_size):
            f.write(data)
            
    print(f"Téléchargement terminé : {filename}")

if __name__ == "__main__":
    url = "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_0.gguf"
    filename = "backend/llm_models/codellama-7b-instruct-q4_0.gguf"
    
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    print("Début du téléchargement...")
    download_file(url, filename) 