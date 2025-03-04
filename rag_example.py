import os
import sys
import json
from pathlib import Path

# Configuration des chemins d'importation
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)  # Pour accéder à settings.py
sys.path.append(os.path.dirname(root_dir))  # Pour accéder au dossier contenant src

# Import des modules
from settings import PATH_CONFIG
from src.rag_manager import RAGManager

def print_json(data):
    """Affiche des données JSON formatées."""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    """
    Exemple d'utilisation du RAGManager pour effectuer des recherches et obtenir des statistiques.
    """
    # Configuration des chemins
    vector_db_dir = PATH_CONFIG['vector_db']
    data_dir = PATH_CONFIG['data']
    
    print("=== Exemple d'utilisation du RAGManager ===")
    
    # Initialiser le RAG Manager
    rag_manager = RAGManager(
        vector_db_dir=vector_db_dir,
        data_dir=data_dir
    )
    
    # Charger la base vectorielle
    print("Chargement de la base vectorielle...")
    if not rag_manager.load_vectordb():
        print("Erreur: Impossible de charger la base vectorielle.")
        print("Exécutez d'abord initialize_vectordb.py pour créer la base.")
        sys.exit(1)
    
    print("Base vectorielle chargée avec succès!")
    
    # Récupérer des statistiques
    print("\n=== Statistiques de la base vectorielle ===")
    stats = rag_manager.get_statistics()
    if stats["status"] == "ok":
        print(f"Nombre de documents: {stats['document_count']}")
        print(f"Sources uniques: {stats['unique_sources']}")
        
        print("\nExtensions de fichiers:")
        for ext, count in stats["extensions"].items():
            print(f"  {ext}: {count} documents")
        
        print("\nTop 5 des sources les plus fréquentes:")
        top_sources = list(stats["top_sources"].items())[:5]
        for source, count in top_sources:
            print(f"  {source}: {count} documents")
    else:
        print(f"Erreur: {stats.get('message', 'Erreur inconnue')}")
    
    # Effectuer une recherche
    print("\n=== Recherche dans la base vectorielle ===")
    query = "Comment implémenter un formulaire de connexion avec validation dans Flutter"
    print(f"Requête: '{query}'")
    
    # Rechercher du contexte
    _, results = rag_manager.search_context(query, k=3)
    
    if results:
        print(f"\nRésultats ({len(results)}):")
        for i, res in enumerate(results):
            source = os.path.basename(res["source"]) if isinstance(res["source"], str) else "Inconnue"
            print(f"\n--- Résultat {i+1} (Source: {source}) ---")
            # Afficher un extrait du contenu
            content = res["contenu"]
            if len(content) > 200:
                content = content[:200] + "..."
            print(content)
    else:
        print("Aucun résultat trouvé.")
    
    # Recherche avec filtrage par extension
    print("\n=== Recherche filtrée par extension ===")
    extension = "dart"
    print(f"Requête: '{query}' (filtré par .{extension})")
    
    # Rechercher du contexte filtré
    _, filtered_results = rag_manager.filter_by_extension(extension, query, k=3)
    
    if filtered_results:
        print(f"\nRésultats filtrés ({len(filtered_results)}):")
        for i, res in enumerate(filtered_results):
            source = os.path.basename(res["source"]) if isinstance(res["source"], str) else "Inconnue"
            print(f"\n--- Résultat {i+1} (Source: {source}) ---")
            # Afficher un extrait du contenu
            content = res["contenu"]
            if len(content) > 200:
                content = content[:200] + "..."
            print(content)
    else:
        print("Aucun résultat filtré trouvé.")
    
    print("\n=== Fin de l'exemple ===")

if __name__ == "__main__":
    main()