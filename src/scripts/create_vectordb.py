import os
import time
import sys
from pathlib import Path
import logging
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import shutil

# Ajout du répertoire parent au PYTHONPATH pour trouver le module settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import PATH_CONFIG

# Configuration
BASE_DIR = PATH_CONFIG['base']
DATA_DIR = PATH_CONFIG['data']
VECTORDB_DIR = PATH_CONFIG['vector_db']

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{BASE_DIR}/vectordb_creation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VectorDB")

# Créer le dossier pour la base vectorielle
os.makedirs(VECTORDB_DIR, exist_ok=True)

def charger_documents_code():
    """Charge les documents de code depuis le dossier des projets."""
    logger.info("Chargement des documents de code...")
    
    # Extensions à prendre en compte pour les fichiers de code
    code_extensions = [
        "dart", "java", "kt", "gradle", "xml", "yaml", "json", 
        "md", "txt", "properties"
    ]
    
    all_documents = []
    total_files = 0
    
    # Pour chaque extension, charger les fichiers correspondants
    for ext in code_extensions:
        try:
            loader = DirectoryLoader(
                f"{DATA_DIR}/projets", 
                glob=f"**/*.{ext}", 
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8", "autodetect_encoding": True},
                show_progress=True
            )
            docs = loader.load()
            logger.info(f"Chargés {len(docs)} fichiers .{ext}")
            all_documents.extend(docs)
            total_files += len(docs)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des fichiers .{ext}: {str(e)}")
    
    logger.info(f"Total: {total_files} fichiers de code chargés")
    return all_documents

def charger_documents_documentation():
    """Charge les documents de documentation."""
    logger.info("Chargement de la documentation...")
    
    try:
        # Documentation Flutter et Android
        loader = DirectoryLoader(
            f"{DATA_DIR}/documentation", 
            glob=f"**/*.json", 
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8", "autodetect_encoding": True},
            show_progress=True
        )
        docs = loader.load()
        logger.info(f"Chargés {len(docs)} fichiers de documentation")
        return docs
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la documentation: {str(e)}")
        return []

def decouper_documents(documents):
    """Découpe les documents en chunks pour faciliter la vectorisation."""
    logger.info(f"Découpage de {len(documents)} documents...")
    
    # Paramètres de découpage adaptés au code
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,            # Taille de chaque chunk
        chunk_overlap=200,          # Chevauchement pour maintenir le contexte
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunks = splitter.split_documents(documents)
    logger.info(f"Documents découpés en {len(chunks)} chunks")
    
    # Afficher des statistiques sur les chunks
    chunk_sizes = [len(chunk.page_content) for chunk in chunks]
    avg_size = sum(chunk_sizes) / len(chunks) if chunks else 0
    
    logger.info(f"Taille moyenne des chunks: {avg_size:.2f} caractères")
    logger.info(f"Plus petit chunk: {min(chunk_sizes)} caractères")
    logger.info(f"Plus grand chunk: {max(chunk_sizes)} caractères")
    
    return chunks

def creer_base_vectorielle(chunks):
    """Crée la base vectorielle à partir des chunks."""
    logger.info("Création de la base vectorielle...")
    start_time = time.time()
    
    # Utiliser un modèle d'embedding léger
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}  # Utiliser CPU à la place de GPU
    )
    
    # Supprimer la base existante si nécessaire
    if os.path.exists(f"{VECTORDB_DIR}/chroma"):
        logger.info("Suppression de la base vectorielle existante...")
        shutil.rmtree(f"{VECTORDB_DIR}/chroma")
    
    # Créer la base
    logger.info(f"Vectorisation de {len(chunks)} chunks...")
    
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=f"{VECTORDB_DIR}/chroma"
    )
    
    # Sauvegarder la base
    vectordb.persist()
    
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info(f"Base vectorielle créée et sauvegardée dans {VECTORDB_DIR}/chroma")
    logger.info(f"Temps de création: {duration:.2f} secondes")
    
    return vectordb

def tester_recherche(vectordb):
    """Teste la recherche dans la base vectorielle avec quelques requêtes."""
    logger.info("Test de recherche dans la base vectorielle...")
    
    # Quelques requêtes de test
    test_queries = [
        "Comment créer une page de connexion dans Flutter",
        "Comment implémenter une liste déroulante avec recherche",
        "Comment gérer l'authentification avec Firebase",
        "Comment créer une interface adaptative pour différentes tailles d'écran"
    ]
    
    for query in test_queries:
        logger.info(f"Requête: '{query}'")
        
        # Effectuer la recherche
        docs = vectordb.similarity_search(query, k=2)
        
        # Afficher les résultats
        for i, doc in enumerate(docs):
            logger.info(f"Résultat {i+1}:")
            logger.info(f"Source: {doc.metadata.get('source', 'Inconnue')}")
            logger.info(f"Contenu: {doc.page_content[:100]}...")
            logger.info("---")

def main():
    logger.info("=== Création de la base vectorielle RAG ===")
    
    # Charger les documents de code
    code_docs = charger_documents_code()
    
    # Charger la documentation
    doc_docs = charger_documents_documentation()
    
    # Combiner tous les documents
    all_docs = code_docs + doc_docs
    logger.info(f"Total de {len(all_docs)} documents chargés")
    
    # Découper les documents
    chunks = decouper_documents(all_docs)
    
    # Créer la base vectorielle
    vectordb = creer_base_vectorielle(chunks)
    
    # Tester la recherche
    tester_recherche(vectordb)
    
    logger.info("=== Création de la base vectorielle terminée ===")

if __name__ == "__main__":
    main()