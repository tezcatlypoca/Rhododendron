import os
import sys
import argparse
from pathlib import Path

# Configuration des chemins d'importation
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)  # Pour accéder à settings.py
sys.path.append(os.path.dirname(root_dir))  # Pour accéder au dossier contenant src

# Import des modules
from settings import PATH_CONFIG
from src.rag_manager import RAGManager

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Initialise la base vectorielle RAG pour Flutter/Java")
    
    parser.add_argument(
        "--source",
        type=str,
        help="Répertoire source contenant les projets à indexer",
        default=None
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force la recréation de la base vectorielle même si elle existe déjà"
    )
    
    parser.add_argument(
        "--extensions",
        type=str,
        nargs="+",
        help="Extensions de fichiers à inclure",
        default=["dart", "java", "kt", "gradle", "xml", "yaml", "json", "md", "txt", "properties"]
    )
    
    parser.add_argument(
        "--exclude",
        type=str,
        nargs="+",
        help="Dossiers à exclure",
        default=["node_modules", ".git", ".idea", "build", "dist", ".dart_tool", ".pub-cache"]
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Taille des chunks pour la vectorisation",
        default=1000
    )
    
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        help="Chevauchement entre chunks",
        default=200
    )
    
    return parser.parse_args()

def main():
    """
    Initialise la base vectorielle RAG pour Flutter/Java.
    """
    # Récupérer les arguments
    args = parse_args()
    
    # Configuration des chemins
    base_dir = PATH_CONFIG['base']
    data_dir = PATH_CONFIG['data']
    projets_dir = PATH_CONFIG['projets']
    doc_dir = PATH_CONFIG['documentation']
    vector_db_dir = PATH_CONFIG['vector_db']
    
    print(f"=== Initialisation de la base vectorielle RAG ===")
    print(f"Base: {base_dir}")
    print(f"Data: {data_dir}")
    print(f"Projets: {projets_dir}")
    print(f"Documentation: {doc_dir}")
    print(f"Base vectorielle: {vector_db_dir}")
    
    # Utiliser un dossier source spécifique si fourni
    source_dir = args.source if args.source else projets_dir
    print(f"Répertoire source: {source_dir}")
    
    # Vérifier que les répertoires existent
    if not os.path.exists(source_dir):
        print(f"Erreur: Le répertoire source {source_dir} n'existe pas.")
        sys.exit(1)
    
    if not os.path.exists(doc_dir) and os.path.exists(f"{data_dir}/documentation"):
        doc_dir = f"{data_dir}/documentation"
        print(f"Utilisation du répertoire de documentation alternatif: {doc_dir}")
    
    # Initialiser le RAG Manager
    rag_manager = RAGManager(
        vector_db_dir=vector_db_dir,
        data_dir=data_dir,
        excluded_dirs=args.exclude
    )
    
    # Vérifier si la base vectorielle existe déjà
    vectordb_exists = os.path.exists(os.path.join(vector_db_dir, "chroma"))
    if vectordb_exists and not args.force:
        print("La base vectorielle existe déjà.")
        print("Utilisez --force pour la recréer.")
        
        # Charger la base existante pour un test
        print("Test de la base existante...")
        if rag_manager.load_vectordb():
            stats = rag_manager.get_statistics()
            if stats["status"] == "ok":
                print(f"Base vectorielle existante contient {stats['document_count']} documents.")
                test_results = rag_manager.test_search()
                print("Test de recherche réussi.")
                sys.exit(0)
    
    print("Création de la base vectorielle...")
    
    # Charger les documents de code
    print(f"Chargement des documents depuis {source_dir}...")
    code_docs = rag_manager.load_code_documents(source_dir, args.extensions)
    
    if len(code_docs) == 0:
        print("Aucun document de code trouvé. Vérifiez le répertoire source et les extensions.")
        sys.exit(1)
    
    # Charger la documentation si disponible
    doc_docs = []
    if os.path.exists(doc_dir):
        print(f"Chargement de la documentation depuis {doc_dir}...")
        doc_docs = rag_manager.load_documentation(doc_dir)
        print(f"Chargés {len(doc_docs)} documents de documentation.")
    
        # Charger également les documents non-JSON de la documentation
        doc_code_docs = rag_manager.load_code_documents(doc_dir, args.extensions)
        print(f"Chargés {len(doc_code_docs)} fichiers de code additionnels depuis la documentation.")
        doc_docs.extend(doc_code_docs)
    else:
        print(f"Répertoire de documentation {doc_dir} non trouvé. Seuls les documents de code seront utilisés.")
    
    # Combiner tous les documents
    all_docs = code_docs + doc_docs
    print(f"Total: {len(all_docs)} documents chargés.")
    
    # Créer la base vectorielle
    print("Création de la base vectorielle...")
    success = rag_manager.create_vectordb(
        all_docs,
        force_recreate=args.force,
        max_chunks=15000  # Limiter le nombre de chunks pour éviter les problèmes de mémoire
    )
    
    if success:
        print("Base vectorielle créée avec succès!")
        
        # Charger la base pour les statistiques
        rag_manager.load_vectordb()
        stats = rag_manager.get_statistics()
        if stats["status"] == "ok":
            print(f"La base contient {stats['document_count']} documents.")
        
        # Tester la recherche
        print("Test de la base vectorielle...")
        test_results = rag_manager.test_search()
        print("Tests terminés.")
    else:
        print("Erreur lors de la création de la base vectorielle.")
        sys.exit(1)
    
    print("=== Initialisation terminée ===")

if __name__ == "__main__":
    main()