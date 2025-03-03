import os
import sys
import time
import logging
import shutil
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime

# Configuration du chemin de recherche
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'src'))

# Imports pour la vectorisation
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# Imports supplémentaires
import numpy as np
import chromadb
from chromadb.config import Settings

# Importer les paramètres
from settings import PATH_CONFIG

# Chargement de la configuration
try:
    config_path = os.path.join(root_dir, 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        CONFIG = yaml.safe_load(file)
except FileNotFoundError:
    print(f"Fichier config.yaml non trouvé à {config_path}")
    CONFIG = {
        "app": {"name": "Crew AI Locale", "debug": True},
        "database": {"type": "sqlite"}
    }

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(root_dir, 'vectordb_creation.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger("Vectorisation")

class VectorizationQualityMetrics:
    """
    Classe pour évaluer la qualité de la vectorisation.
    """
    @staticmethod
    def calculate_embedding_coherence(embeddings: np.ndarray) -> Dict[str, float]:
        """
        Calcule des métriques de cohérence des embeddings.
        """
        if embeddings is None or len(embeddings) == 0:
            return {}
        
        variance_per_dim = np.var(embeddings, axis=0)
        
        return {
            "embedding_variance": float(np.mean(variance_per_dim)),
            "embedding_stability": float(np.std(variance_per_dim)),
            "total_variance": float(np.var(embeddings)),
            "embedding_coverage": len(embeddings) / 20000
        }
    
    @staticmethod
    def evaluate_search_quality(results: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Évalue la qualité des résultats de recherche.
        """
        if not results:
            return {}
        
        distances = [res.get('score', 0) for res in results]
        
        return {
            "avg_distance": float(np.mean(distances)),
            "max_distance": float(np.max(distances)),
            "min_distance": float(np.min(distances)),
            "distance_variance": float(np.std(distances))
        }

class Vectorisation:
    """
    Classe centralisée pour la gestion de la vectorisation des documents.
    """
    
    def __init__(self, 
                 vector_db_dir: str, 
                 data_dir: Optional[str] = None,
                 embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialise le gestionnaire de vectorisation.
        """
        self.vector_db_dir = vector_db_dir
        self.data_dir = data_dir
        
        # Configuration des répertoires exclus
        self.excluded_dirs = [
            'node_modules', '.git', '.idea', 'build', 'dist', 
            '.dart_tool', '.pub-cache', 'venv', '__pycache__'
        ]
        
        # Modèle d'embedding avec options avancées
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={
                'device': 'cpu',  # Possibilité de passer à 'cuda' si GPU disponible
                'trust_remote_code': True
            }
        )
        
        # Extensions supportées pour le code
        self.code_extensions = [
            ".dart", ".java", ".kt", ".gradle", 
            ".xml", ".yaml", ".json", ".md",
            ".txt", ".properties", ".py", ".js"
        ]
        
        # Base vectorielle et métriques
        self.vectordb = None
        self.quality_metrics = {
            "embedding_coherence": {},
            "search_quality": {}
        }
    
    def _find_files_with_ext(self, base_dir: str, extension: str) -> List[str]:
        """
        Trouve tous les fichiers avec une extension donnée en excluant certains dossiers.
        """
        files = []
        if not os.path.exists(base_dir):
            logger.warning(f"Répertoire non trouvé : {base_dir}")
            return files
            
        for root, dirs, filenames in os.walk(base_dir):
            # Exclure les dossiers non désirés
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for filename in filenames:
                if filename.endswith(extension):
                    file_path = os.path.join(root, filename)
                    files.append(file_path)
        return files
    
    def load_documents(self, source_dir: str, extensions: Optional[List[str]] = None) -> List[Document]:
        """
        Charge les documents depuis un dossier source.
        """
        if not extensions:
            extensions = self.code_extensions
            
        logger.info(f"Chargement des documents depuis {source_dir}...")
        all_documents = []
        
        for ext in extensions:
            # Nettoyer l'extension (avec ou sans point)
            ext_clean = ext[1:] if ext.startswith('.') else ext
            ext_with_dot = f".{ext_clean}"
            
            try:
                # Trouver les fichiers avec l'extension spécifiée
                file_paths = self._find_files_with_ext(source_dir, ext_with_dot)
                
                # Charger chaque fichier individuellement
                docs = []
                for file_path in file_paths:
                    try:
                        loader = TextLoader(file_path, encoding="utf-8", autodetect_encoding=True)
                        docs.extend(loader.load())
                    except Exception as e:
                        logger.error(f"Erreur lors du chargement du fichier {file_path}: {str(e)}")
                
                logger.info(f"Chargés {len(docs)} fichiers {ext_with_dot}")
                all_documents.extend(docs)
            except Exception as e:
                logger.error(f"Erreur lors du chargement des fichiers {ext_with_dot}: {str(e)}")
        
        logger.info(f"Total: {len(all_documents)} fichiers chargés")
        return all_documents
    
    def load_vectordb(self) -> bool:
        """
        Charge la base vectorielle existante.
        """
        try:
            # Vérifier si le fichier SQLite de la base vectorielle existe
            sqlite_path = os.path.join(self.vector_db_dir, "chroma.sqlite3")
            
            if not os.path.exists(sqlite_path):
                logger.error(f"Base vectorielle non trouvée: {sqlite_path}")
                return False
            
            logger.info("Chargement de la base vectorielle...")
            self.vectordb = Chroma(
                persist_directory=self.vector_db_dir,
                embedding_function=self.embedding_model
            )
            
            logger.info(f"Base vectorielle chargée avec succès.")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la base vectorielle: {str(e)}")
            return False

    def add_documents(self, new_documents: List[Document]) -> bool:
        """
        Ajoute de nouveaux documents à la base vectorielle existante.
        """
        if not self.vectordb:
            loaded = self.load_vectordb()
            if not loaded:
                logger.error("Impossible de charger la base vectorielle pour l'ajout de documents")
                return False
        
        try:
            logger.info(f"Ajout de {len(new_documents)} nouveaux documents à la base vectorielle...")
            
            # Vérifier si des documents ont été fournis
            if not new_documents:
                logger.warning("Aucun document à ajouter.")
                return False
            
            # Découper les documents en chunks
            chunks = self.split_documents(new_documents)
            
            # Vérifier si des chunks ont été créés
            if not chunks:
                logger.warning("Aucun chunk créé à partir des documents.")
                return False
                
            # Ajouter les chunks à la base
            self.vectordb.add_documents(chunks)
            
            logger.info(f"Documents ajoutés avec succès.")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de documents: {str(e)}")
            return False
    
    def split_documents(self, documents: List[Document], 
                       chunk_size: int = 1000, 
                       chunk_overlap: int = 200) -> List[Document]:
        """
        Découpe les documents en chunks pour faciliter la vectorisation.
        """
        logger.info(f"Découpage de {len(documents)} documents...")
        
        if not documents:
            logger.warning("Aucun document à découper.")
            return []
        
        # Paramètres de découpage adaptés au code
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        chunks = splitter.split_documents(documents)
        logger.info(f"Documents découpés en {len(chunks)} chunks")
        
        # Afficher des statistiques sur les chunks
        if chunks:
            chunk_sizes = [len(chunk.page_content) for chunk in chunks]
            avg_size = sum(chunk_sizes) / len(chunks)
            
            logger.info(f"Taille moyenne des chunks: {avg_size:.2f} caractères")
            logger.info(f"Plus petit chunk: {min(chunk_sizes)} caractères")
            logger.info(f"Plus grand chunk: {max(chunk_sizes)} caractères")
        
        return chunks
    
    def create_vectordb(self, 
                   documents: List[Document], 
                   force_recreate: bool = False,
                   max_chunks: int = 10000) -> bool:
        """
        Crée la base vectorielle à partir des documents.
        """
        try:
            logger.info("Création de la base vectorielle...")
            start_time = time.time()
            
            if not documents:
                logger.error("Aucun document fourni pour la création de la base vectorielle.")
                return False
            
            # Découper les documents en chunks
            chunks = self.split_documents(documents)
            
            if not chunks:
                logger.error("Aucun chunk créé à partir des documents.")
                return False
            
            # Supprimer la base existante si nécessaire
            sqlite_path = os.path.join(self.vector_db_dir, "chroma.sqlite3")
            if force_recreate and os.path.exists(sqlite_path):
                logger.info("Suppression de la base vectorielle existante...")
                # Suppression du fichier SQLite
                os.remove(sqlite_path)
                
                # Suppression des dossiers UUID s'ils existent
                for item in os.listdir(self.vector_db_dir):
                    item_path = os.path.join(self.vector_db_dir, item)
                    if os.path.isdir(item_path) and len(os.path.basename(item_path)) == 36:
                        # Si c'est un dossier avec un nom qui ressemble à un UUID
                        shutil.rmtree(item_path)
            
            # Limiter le nombre de chunks
            if len(chunks) > max_chunks:
                logger.warning(f"Nombre de chunks ({len(chunks)}) supérieur à {max_chunks}. Limitation.")
                chunks = chunks[:max_chunks]
                logger.info(f"Utilisation des {len(chunks)} premiers chunks")
            
            # Créer et persister la base
            os.makedirs(self.vector_db_dir, exist_ok=True)
            
            logger.info(f"Vectorisation de {len(chunks)} chunks...")
            self.vectordb = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding_model,
                persist_directory=self.vector_db_dir
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"Base vectorielle créée et sauvegardée dans {self.vector_db_dir}")
            logger.info(f"Temps de création: {duration:.2f} secondes")
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la création de la base vectorielle: {str(e)}")
            return False
    
    def search_similar(self, query: str, k: int = 5) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Recherche des documents similaires avec leurs scores.
        """
        # Charger la base si nécessaire
        if not self.vectordb:
            loaded = self.load_vectordb()
            if not loaded:
                logger.error("Base vectorielle non chargée. Impossible d'effectuer la recherche.")
                return "", []
        
        try:
            logger.info(f"Recherche de contexte pour: '{query}'")
            
            # Effectuer la recherche avec calcul des scores
            results = self.vectordb.similarity_search_with_score(query, k=k)
            
            # Extraire le contenu et les métadonnées
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "contenu": doc.page_content,
                    "source": doc.metadata.get("source", "Inconnue"),
                    "score": score
                })
            
            # Formatter le contexte
            contexte = ""
            for i, res in enumerate(formatted_results):
                source = os.path.basename(res["source"]) if isinstance(res["source"], str) else "Inconnue"
                score = f" (score: {res['score']:.4f})" if "score" in res else ""
                contexte += f"--- Document {i+1} (Source: {source}){score} ---\n"
                contexte += res["contenu"] + "\n\n"
            
            logger.info(f"Contexte trouvé: {len(formatted_results)} documents")
            return contexte, formatted_results
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de contexte: {str(e)}")
            return "", []
    
    def update_from_directory(self, directory: str, 
                            extensions: Optional[List[str]] = None,
                            recreate: bool = False) -> bool:
        """
        Met à jour la base vectorielle à partir d'un dossier.
        """
        try:
            logger.info(f"Mise à jour de la base vectorielle depuis {directory}...")
            
            # Charger les documents
            documents = self.load_documents(directory, extensions)
            
            if not documents:
                logger.warning(f"Aucun document trouvé dans {directory}")
                return False
            
            # Vérifier si la base existe déjà
            base_exists = os.path.exists(os.path.join(self.vector_db_dir, "chroma"))
            
            if recreate or not base_exists:
                # Créer une nouvelle base
                return self.create_vectordb(documents, force_recreate=recreate)
            else:
                # Ajouter à la base existante
                return self.add_documents(documents)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour depuis {directory}: {str(e)}")
            return False

def main():
    # Action par défaut
    action = sys.argv[1] if len(sys.argv) > 1 else "test"
    
    # Chemins de la base vectorielle et des données
    vector_db_dir = os.path.normpath(PATH_CONFIG['vector_db'])  # Normaliser le chemin
    projets_dir = os.path.normpath(PATH_CONFIG['projets'])      # Normaliser le chemin
    
    print(f"Chemin de la base vectorielle: {vector_db_dir}")
    print(f"Chemin des projets: {projets_dir}")
    
    # Initialiser le système de vectorisation
    vectorizer = Vectorisation(
        vector_db_dir=vector_db_dir, 
        data_dir=projets_dir
    )
    
    # Actions possibles
    if action == "load":
        # Charger la base vectorielle
        logger.info("Chargement de la base vectorielle...")
        success = vectorizer.load_vectordb()
        logger.info(f"Chargement : {'Réussi' if success else 'Échoué'}")
    
    elif action == "update":
        # Mettre à jour depuis un répertoire
        logger.info("Mise à jour de la base vectorielle...")
        success = vectorizer.update_from_directory(projets_dir, recreate=False)
        logger.info(f"Mise à jour : {'Réussie' if success else 'Échouée'}")
    
    elif action == "search":
        # Effectuer une recherche de test
        query = "Comment créer une application Flutter modulaire"
        logger.info(f"Recherche de contexte pour : {query}")
        contexte, results = vectorizer.search_similar(query)
        
        print("Résultats de recherche :")
        print(contexte)
    
    else:
        # Action par défaut : informations de base
        logger.info("Actions disponibles : load, update, search")
        print("Utilisation : python vectorisation.py [load|update|search]")

if __name__ == "__main__":
    main()