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
import glob

# Ajout du répertoire parent au PYTHONPATH pour trouver le module settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import PATH_CONFIG

# Configuration
BASE_DIR = PATH_CONFIG['base']
DATA_DIR = PATH_CONFIG['data']
VECTORDB_DIR = PATH_CONFIG['vector_db']

# Dossiers à exclure
EXCLUDED_DIRS = ['node_modules', '.git', '.idea', 'build', 'dist', '.dart_tool', '.pub-cache']

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

def should_exclude(file_path):
    """Vérifie si un fichier doit être exclu en fonction de son chemin."""
    normalized_path = file_path.replace("\\", "/")
    for excluded_dir in EXCLUDED_DIRS:
        if f"/{excluded_dir}/" in normalized_path:
            return True
    return False

def find_files_with_ext(base_dir, extension):
    """Trouve tous les fichiers avec une extension donnée en excluant certains dossiers."""
    files = []
    for root, dirs, filenames in os.walk(base_dir):
        # Modification sur place pour ne pas descendre dans les dossiers exclus
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for filename in filenames:
            if filename.endswith(f".{extension}"):
                file_path = os.path.join(root, filename)
                files.append(file_path)
    return files

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
            # Trouver les fichiers en excluant les dossiers non désirés
            file_paths = find_files_with_ext(f"{DATA_DIR}/projets", ext)
            
            # Charger chaque fichier individuellement
            docs = []
            for file_path in file_paths:
                try:
                    loader = TextLoader(file_path, encoding="utf-8", autodetect_encoding=True)
                    docs.extend(loader.load())
                except Exception as e:
                    logger.error(f"Erreur lors du chargement du fichier {file_path}: {str(e)}")
            
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
    logger.info(f"Plus petit chunk: {min(chunk_sizes) if chunk_sizes else 0} caractères")
    logger.info(f"Plus grand chunk: {max(chunk_sizes) if chunk_sizes else 0} caractères")
    
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
    
    # Limiter le nombre de chunks si nécessaire pour éviter les problèmes de mémoire
    max_chunks = 10000  # Vous pouvez ajuster ce nombre en fonction de votre RAM
    if len(chunks) > max_chunks:
        logger.warning(f"Nombre de chunks ({len(chunks)}) supérieur à {max_chunks}. Limitation pour éviter les problèmes de mémoire.")
        chunks = chunks[:max_chunks]
        logger.info(f"Utilisation des {len(chunks)} premiers chunks pour la vectorisation.")
    
    vectordb = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=f"{VECTORDB_DIR}/chroma"
    )
    

    
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