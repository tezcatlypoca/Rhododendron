import os
import sys
import json
from datetime import datetime

# Ajouter le chemin du projet au PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import yaml
import numpy as np
import chromadb
from chromadb.config import Settings

from settings import PATH_CONFIG

def explain_embeddings():
    """
    Explication détaillée des embeddings et de leur utilisation.
    """
    print("\n🧠 COMPRENDRE LES EMBEDDINGS 🧠")
    print("=" * 50)
    
    print("\n1. Qu'est-ce qu'un embedding ? 🤔")
    print("Un embedding est une représentation vectorielle dense de données textuelles,")
    print("où chaque mot ou document est transformé en un vecteur de nombres réels.")
    print("C'est comme une 'empreinte numérique' qui capture le sens et le contexte.")
    
    print("\n2. Comment fonctionnent les embeddings ? 🔍")
    print("- Transformation : Chaque mot/document est converti en un vecteur de nombres")
    print("- Similarité sémantique : Des mots/documents similaires ont des vecteurs proches")
    print("- Dimension typique : Souvent entre 100 et 1000 dimensions")
    
    print("\n3. Avantages des embeddings 🚀")
    print("- Capture du contexte et du sens")
    print("- Possibilité de calculs mathématiques sur le texte")
    print("- Permet la recherche sémantique et la recommandation")
    
    print("\n4. Exemple simplifié 📊")
    print("Vecteur pour 'roi'   : [0.2, -0.5, 0.1, ...]")
    print("Vecteur pour 'reine' : [0.21, -0.49, 0.12, ...]")
    print("Ces vecteurs seraient très proches, reflétant leur similarité sémantique")
    
    print("\n5. Dans votre projet 🤖")
    print("- Modèle utilisé : sentence-transformers/all-MiniLM-L6-v2")
    print("- Transforme le code source, documentation en vecteurs")
    print("- Permet de rechercher du code similaire par sens, pas seulement par mots-clés")

def safe_get_embeddings(collection):
    """
    Récupère les embeddings de manière sécurisée.
    """
    try:
        results = collection.get(include=['embeddings'])
        
        if not results or 'embeddings' not in results:
            print("Aucun embedding disponible.")
            return None
        
        embeddings = results['embeddings']
        return np.array(embeddings)
    
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des embeddings : {e}")
        return None

def perform_semantic_search_test(collection):
    """
    Test de recherche sémantique pour vérifier la qualité des embeddings.
    """
    print("\n🔍 TEST DE RECHERCHE SÉMANTIQUE AVANCÉ")
    print("=" * 50)
    
    # Requêtes de test avec différents niveaux de similitude
    test_queries = [
        "Comment créer une application Flutter simple et modulaire",
        "Gestion des états dans une application mobile",
        "Intégration d'API REST en développement mobile",
        "Architecture de code propre et maintenable"
    ]
    
    print("\n📋 Requêtes de test :")
    for query in test_queries:
        print(f"\n🔎 Requête : '{query}'")
        
        try:
            # Effectuer une recherche sémantique
            results = collection.query(
                query_texts=[query],
                n_results=3,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Afficher les résultats
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            ), 1):
                print(f"\n  Résultat {i} :")
                print(f"    Source : {metadata.get('source', 'Inconnue')}")
                print(f"    Distance : {distance:.4f}")
                print(f"    Extrait : {doc[:200]}..." if len(doc) > 200 else f"    Extrait : {doc}")
        
        except Exception as e:
            print(f"❌ Erreur lors de la recherche pour '{query}' : {e}")

def inspect_vector_database(vector_db_path):
    """
    Inspecte en profondeur la base vectorielle Chroma.
    """
    print("\n=== 🔬 INSPECTION DÉTAILLÉE DE LA BASE VECTORIELLE ===")
    
    # Initialiser le client Chroma
    chroma_client = chromadb.PersistentClient(
        path=vector_db_path, 
        settings=Settings(allow_reset=True)
    )
    
    # Récupérer les noms des collections
    collection_names = chroma_client.list_collections()
    print(f"\n📋 Nombre de collections : {len(collection_names)}")
    
    for collection_name in collection_names:
        try:
            # Récupérer la collection
            collection = chroma_client.get_collection(collection_name)
            
            print(f"\n🗂️ Collection : {collection_name}")
            
            # Informations de base
            doc_count = collection.count()
            print(f"  Nombre de documents : {doc_count}")
            
            # Analyse des embeddings
            embeddings = safe_get_embeddings(collection)
            
            # Test de recherche sémantique
            perform_semantic_search_test(collection)
        
        except Exception as e:
            print(f"❌ Erreur lors de l'inspection de la collection {collection_name}: {e}")

def main():
    print("🚀 Diagnostic Complet du Système de Vectorisation")
    
    # Explication des embeddings
    explain_embeddings()
    
    # Chemin de la base vectorielle
    vector_db_dir = PATH_CONFIG['vector_db']
    print(f"\nRépertoire de la base vectorielle : {vector_db_dir}")
    
    try:
        # Inspecter la base vectorielle
        inspect_vector_database(vector_db_dir)

    except Exception as e:
        print(f"❌ Erreur lors de l'inspection de la base vectorielle : {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()