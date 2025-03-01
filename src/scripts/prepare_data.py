import os
import sys
import shutil
import requests
import zipfile
import io
from pathlib import Path

# Ajout du répertoire parent au PYTHONPATH pour trouver le module settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import PATH_CONFIG

# Configuration des chemins
BASE_DIR = PATH_CONFIG['base']
DATA_DIR = PATH_CONFIG['data']
PROJETS_DIR = PATH_CONFIG['projets']
DOC_DIR = PATH_CONFIG['documentation']

# Création des dossiers nécessaires
os.makedirs(PROJETS_DIR, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)

def copier_projets_existants(source_dir, dest_dir):
    """Copie les projets Flutter/Java existants vers le dossier de données."""
    # Remplacer ces extensions par celles utilisées dans vos projets
    extensions = ['.java', '.dart', '.yaml', '.xml', '.gradle', '.json', '.md']
    
    print(f"Copie des projets depuis {source_dir} vers {dest_dir}...")
    
    # Itérer à travers les dossiers de projets
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # Vérifier si l'extension est dans la liste des extensions à copier
            if any(file.endswith(ext) for ext in extensions):
                # Chemin du fichier source
                source_file = os.path.join(root, file)
                
                # Chemin relatif pour maintenir la structure
                rel_path = os.path.relpath(source_file, source_dir)
                
                # Chemin de destination
                dest_file = os.path.join(dest_dir, rel_path)
                
                # Créer les dossiers nécessaires
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                
                # Copier le fichier
                shutil.copy2(source_file, dest_file)
    
    print("Copie terminée.")

def telecharger_documentation():
    """Télécharge la documentation Flutter et Java."""
    # URL de documentation Flutter
    flutter_doc_url = "https://api.flutter.dev/flutter/index.json"
    
    # URL de documentation Android/Java
    android_doc_url = "https://developer.android.com/reference/androidx/classes.zip"
    
    print("Téléchargement de la documentation Flutter...")
    try:
        # Télécharger la documentation Flutter
        flutter_response = requests.get(flutter_doc_url)
        flutter_response.raise_for_status()
        
        # Enregistrer le fichier
        with open(f"{DOC_DIR}/flutter_index.json", 'wb') as f:
            f.write(flutter_response.content)
        
        print("Documentation Flutter téléchargée avec succès.")
    except Exception as e:
        print(f"Erreur lors du téléchargement de la documentation Flutter: {str(e)}")
    
    print("Téléchargement de la documentation Android...")
    try:
        # Télécharger la documentation Android
        android_response = requests.get(android_doc_url)
        android_response.raise_for_status()
        
        # Créer un dossier pour la documentation Android
        android_dir = f"{DOC_DIR}/android"
        os.makedirs(android_dir, exist_ok=True)
        
        # Extraire le contenu du zip
        with zipfile.ZipFile(io.BytesIO(android_response.content)) as z:
            z.extractall(android_dir)
        
        print("Documentation Android téléchargée avec succès.")
    except Exception as e:
        print(f"Erreur lors du téléchargement de la documentation Android: {str(e)}")

def nettoyer_fichiers():
    """Nettoie les fichiers pour ne garder que le contenu pertinent."""
    # Parcourir tous les fichiers
    for root, dirs, files in os.walk(PROJETS_DIR):
        for file in files:
            # Ignorer les fichiers binaires, les ressources, etc.
            if file.endswith(('.png', '.jpg', '.ttf', '.otf', '.jar', '.class', '.so')):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Supprimé: {file_path}")

def statistiques_donnees():
    """Affiche des statistiques sur les données collectées."""
    extensions_count = {}
    total_files = 0
    total_size = 0
    
    # Parcourir tous les fichiers
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Récupérer l'extension
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            
            # Mettre à jour les compteurs
            if ext not in extensions_count:
                extensions_count[ext] = 0
            extensions_count[ext] += 1
            
            total_files += 1
            total_size += os.path.getsize(file_path)
    
    # Afficher les statistiques
    print("\n=== Statistiques des données ===")
    print(f"Nombre total de fichiers: {total_files}")
    print(f"Taille totale: {total_size / (1024*1024):.2f} MB")
    print("\nRépartition par extension:")
    
    for ext, count in sorted(extensions_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ext}: {count} fichiers")

def main():
    print("=== Préparation des données pour le système RAG ===")
    
    # Demander le chemin source des projets
    source_dir = input("Entrez le chemin vers vos projets Flutter/Java (ex: D:/MesProjets): ")
    
    # Vérifier si le chemin existe
    if not os.path.exists(source_dir):
        print(f"Le chemin {source_dir} n'existe pas.")
        return
    
    # Copier les projets existants
    copier_projets_existants(source_dir, PROJETS_DIR)
    
    # Télécharger la documentation
    telecharger_documentation()
    
    # Nettoyer les fichiers
    nettoyer_fichiers()
    
    # Afficher les statistiques
    statistiques_donnees()
    
    print("\nPréparation des données terminée.")
    print(f"Les données sont prêtes dans {DATA_DIR}")

if __name__ == "__main__":
    main()