import os, sys, time, logging, shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

# Imports mis à jour pour éviter les warnings de dépréciation
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# Configuration des chemins d'importation
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)  # Pour accéder à settings.py
sys.path.append(os.path.dirname(root_dir))  # Pour accéder au dossier contenant src

class RAGManager:
    """
    Gestionnaire pour le système RAG (Retrieval-Augmented Generation).
    Gère le chargement, la création, la mise à jour et l'interrogation de la base vectorielle.
    """
    
    def __init__(self, 
                 vector_db_dir: str, 
                 data_dir: Optional[str] = None,
                 embedding_model: Optional[Any] = None,
                 excluded_dirs: Optional[List[str]] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialise le gestionnaire RAG.
        
        Args:
            vector_db_dir: Chemin vers le répertoire de la base de donnée vectorielle
            data_dir: Chemin vers le répertoire des données (code et documentation)
            embedding_model: Modèle d'embedding à utiliser (par défaut, HuggingFaceEmbeddings)
            excluded_dirs: Liste des répertoires à exclure lors du chargement des documents
            logger: Logger à utiliser (par défaut, crée un nouveau logger)
        """
        self.vector_db_dir = vector_db_dir
        self.data_dir = data_dir
        self.excluded_dirs = excluded_dirs or ['node_modules', '.git', '.idea', 'build', 'dist', '.dart_tool', '.pub-cache']
        
        # Configuration du logger
        self.logger = logger or self._setup_logger()
        
        # Modèle d'embedding
        self.embedding_model = embedding_model or HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Base  de donnée vectorielle
        self.vectordb = None
    
    def _setup_logger(self) -> logging.Logger:
        """Configure et retourne un logger."""
        logger = logging.getLogger("RAGManager")
        logger.setLevel(logging.INFO)
        
        # Vérifier si des handlers sont déjà configurés
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Handler pour la console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # Handler pour un fichier de log
            try:
                file_handler = logging.FileHandler("rag_manager.log")
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Impossible de créer le fichier de log: {str(e)}")
        
        return logger
    
    def load_vectordb(self) -> bool:
        """
        Charge la base vectorielle existante.
        
        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        try:
            # Vérifier si la base vectorielle n'existe pas
            if not os.path.exists(os.path.join(self.vector_db_dir, "chroma")):
                self.logger.error(f"Base vectorielle non trouvée dans {self.vector_db_dir}/chroma")
                return False
            
            self.logger.info("Chargement de la base vectorielle...")
            self.vectordb = Chroma(
                persist_directory=os.path.join(self.vector_db_dir, "chroma"),
                embedding_function=self.embedding_model
            )
            
            self.logger.info(f"Base vectorielle chargée avec succès.")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la base vectorielle: {str(e)}")
            return False
    
    def should_exclude(self, file_path: str) -> bool:
        """
        Vérifie si un fichier doit être exclu en fonction de son chemin.
        
        Args:
            file_path: Chemin du fichier à vérifier
            
        Returns:
            bool: True si le fichier doit être exclu, False sinon
        """
        normalized_path = file_path.replace("\\", "/")
        for excluded_dir in self.excluded_dirs:
            if f"/{excluded_dir}/" in normalized_path:
                return True
        return False
    
    def find_files_with_ext(self, base_dir: str, extension: str) -> List[str]:
        """
        Trouve tous les fichiers avec une extension donnée en excluant certains dossiers.
        
        Args:
            base_dir: Répertoire de base pour la recherche
            extension: Extension de fichier à rechercher (sans le point)
            
        Returns:
            Liste des chemins des fichiers trouvés
        """
        files = []
        for root, dirs, filenames in os.walk(base_dir):
            # Modification sur place pour ne pas descendre dans les dossiers exclus
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for filename in filenames:
                if filename.endswith(f".{extension}"):
                    file_path = os.path.join(root, filename)
                    files.append(file_path)
        return files
    
    def load_code_documents(self, code_dir: str, extensions: Optional[List[str]] = None) -> List[Document]:
        """
        Charge les documents de code depuis le dossier spécifié.
        
        Args:
            code_dir: Répertoire contenant les fichiers de code
            extensions: Liste des extensions de fichier à inclure
            
        Returns:
            Liste des documents chargés
        """
        # Extensions par défaut à prendre en compte pour les fichiers de code
        code_extensions = extensions or [
            "dart", "java", "kt", "gradle", "xml", "yaml", "json", 
            "md", "txt", "properties"
        ]
        
        self.logger.info(f"Chargement des documents de code depuis {code_dir}...")
        
        all_documents = []
        total_files = 0
        
        # Pour chaque extension, charger les fichiers correspondants
        for ext in code_extensions:
            try:
                # Trouver les fichiers en excluant les dossiers non désirés
                file_paths = self.find_files_with_ext(code_dir, ext)
                
                # Charger chaque fichier individuellement
                docs = []
                for file_path in file_paths:
                    try:
                        loader = TextLoader(file_path, encoding="utf-8", autodetect_encoding=True)
                        docs.extend(loader.load())
                    except Exception as e:
                        self.logger.error(f"Erreur lors du chargement du fichier {file_path}: {str(e)}")
                
                self.logger.info(f"Chargés {len(docs)} fichiers .{ext}")
                all_documents.extend(docs)
                total_files += len(docs)
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement des fichiers .{ext}: {str(e)}")
        
        self.logger.info(f"Total: {total_files} fichiers de code chargés")
        return all_documents
    
    def load_documentation(self, doc_dir: str) -> List[Document]:
        """
        Charge les documents de documentation depuis le dossier spécifié.
    
        Args:
            doc_dir: Répertoire contenant la documentation
        
        Returns:
            Liste des documents de documentation
        """
        self.logger.info(f"Chargement de la documentation depuis {doc_dir}...")
    
        all_docs = []
    
        try:
            # Chargement de fichiers JSON (documentation principale)
            json_loader = DirectoryLoader(
                doc_dir, 
                glob=f"**/*.json", 
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8", "autodetect_encoding": True},
                show_progress=True
            )
            json_docs = json_loader.load()
            self.logger.info(f"Chargés {len(json_docs)} fichiers JSON de documentation")
            all_docs.extend(json_docs)
        
            # Chargement de fichiers markdown (documentation additionnelle)
            try:
                md_loader = DirectoryLoader(
                    doc_dir, 
                    glob=f"**/*.md", 
                    loader_cls=TextLoader,
                    loader_kwargs={"encoding": "utf-8", "autodetect_encoding": True},
                    show_progress=True
                )
                md_docs = md_loader.load()
                self.logger.info(f"Chargés {len(md_docs)} fichiers Markdown de documentation")
                all_docs.extend(md_docs)
            except Exception as e:
                self.logger.warning(f"Erreur lors du chargement des fichiers markdown: {str(e)}")
            
            return all_docs
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la documentation: {str(e)}")
            return []
    
    def split_documents(self, documents: List[Document], 
                       chunk_size: int = 1000, 
                       chunk_overlap: int = 200) -> List[Document]:
        """
        Découpe les documents en chunks pour faciliter la vectorisation.
        
        Args:
            documents: Liste des documents à découper
            chunk_size: Taille de chaque chunk
            chunk_overlap: Chevauchement entre chunks consécutifs
            
        Returns:
            Liste des chunks créés
        """
        self.logger.info(f"Découpage de {len(documents)} documents...")
        
        # Paramètres de découpage adaptés au code
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        chunks = splitter.split_documents(documents)
        self.logger.info(f"Documents découpés en {len(chunks)} chunks")
        
        # Afficher des statistiques sur les chunks
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        avg_size = sum(chunk_sizes) / len(chunks) if chunks else 0
        
        self.logger.info(f"Taille moyenne des chunks: {avg_size:.2f} caractères")
        self.logger.info(f"Plus petit chunk: {min(chunk_sizes) if chunk_sizes else 0} caractères")
        self.logger.info(f"Plus grand chunk: {max(chunk_sizes) if chunk_sizes else 0} caractères")
        
        return chunks
    
    def create_vectordb(self, 
                       documents: List[Document], 
                       force_recreate: bool = False,
                       max_chunks: int = 10000) -> bool:
        """
        Crée la base vectorielle à partir des documents.
        
        Args:
            documents: Liste des documents à inclure dans la base
            force_recreate: Si True, supprime la base existante avant d'en créer une nouvelle
            max_chunks: Nombre maximum de chunks à inclure dans la base
            
        Returns:
            bool: True si la création a réussi, False sinon
        """
        try:
            self.logger.info("Création de la base vectorielle...")
            start_time = time.time()
            
            # Découper les documents en chunks
            chunks = self.split_documents(documents)
            
            # Supprimer la base existante si nécessaire
            if force_recreate and os.path.exists(os.path.join(self.vector_db_dir, "chroma")):
                self.logger.info("Suppression de la base vectorielle existante...")
                shutil.rmtree(os.path.join(self.vector_db_dir, "chroma"))
            
            # Limiter le nombre de chunks si nécessaire pour éviter les problèmes de mémoire
            if len(chunks) > max_chunks:
                self.logger.warning(f"Nombre de chunks ({len(chunks)}) supérieur à {max_chunks}. Limitation pour éviter les problèmes de mémoire.")
                chunks = chunks[:max_chunks]
                self.logger.info(f"Utilisation des {len(chunks)} premiers chunks pour la vectorisation.")
            
            # Créer et persister la base
            os.makedirs(self.vector_db_dir, exist_ok=True)
            
            self.logger.info(f"Vectorisation de {len(chunks)} chunks...")
            self.vectordb = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding_model,
                persist_directory=os.path.join(self.vector_db_dir, "chroma")
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.info(f"Base vectorielle créée et sauvegardée dans {self.vector_db_dir}/chroma")
            self.logger.info(f"Temps de création: {duration:.2f} secondes")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de la base vectorielle: {str(e)}")
            return False
    
    def search_context(self, query: str, k: int = 5) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Recherche du contexte pertinent dans la base vectorielle.
        
        Args:
            query: Requête de recherche
            k: Nombre de documents à récupérer
            
        Returns:
            Tuple contenant le contexte formaté et les résultats bruts
        """
        if not self.vectordb:
            loaded = self.load_vectordb()
            if not loaded:
                return "", []
        
        try:
            self.logger.info(f"Recherche de contexte pour: '{query}'")
            documents = self.vectordb.similarity_search(query, k=k)
            
            # Extraire le contenu et les métadonnées
            resultats = []
            for doc in documents:
                resultats.append({
                    "contenu": doc.page_content,
                    "source": doc.metadata.get("source", "Inconnue")
                })
            
            # Formatter le contexte
            contexte = ""
            for i, res in enumerate(resultats):
                source = os.path.basename(res["source"]) if isinstance(res["source"], str) else "Inconnue"
                contexte += f"--- Document {i+1} (Source: {source}) ---\n"
                contexte += res["contenu"] + "\n\n"
            
            self.logger.info(f"Contexte trouvé: {len(resultats)} documents")
            return contexte, resultats
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de contexte: {str(e)}")
            return "", []
    
    def filter_by_extension(self, extension: str, query: str, k: int = 5) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Recherche du contexte en filtrant par extension de fichier.
        
        Args:
            extension: Extension de fichier à filtrer (sans le point)
            query: Requête de recherche
            k: Nombre de documents à récupérer
            
        Returns:
            Tuple contenant le contexte formaté et les résultats bruts
        """
        if not self.vectordb:
            loaded = self.load_vectordb()
            if not loaded:
                return "", []
        
        try:
            self.logger.info(f"Recherche de contexte pour: '{query}' (filtré par .{extension})")
            
            # Créer une fonction de filtrage pour l'extension
            def filter_func(doc):
                source = doc.metadata.get('source', '')
                return source.endswith(f'.{extension}')
            
            # Rechercher avec un nombre plus grand pour permettre le filtrage
            larger_k = k * 3  # Récupérer plus de documents pour avoir assez après filtrage
            documents = self.vectordb.similarity_search(query, k=larger_k)
            
            # Filtrer les documents par extension
            filtered_docs = [doc for doc in documents if filter_func(doc)]
            filtered_docs = filtered_docs[:k]  # Limiter au nombre demandé
            
            # Extraire le contenu et les métadonnées
            resultats = []
            for doc in filtered_docs:
                resultats.append({
                    "contenu": doc.page_content,
                    "source": doc.metadata.get("source", "Inconnue")
                })
            
            # Formatter le contexte
            contexte = ""
            for i, res in enumerate(resultats):
                source = os.path.basename(res["source"]) if isinstance(res["source"], str) else "Inconnue"
                contexte += f"--- Document {i+1} (Source: {source}) ---\n"
                contexte += res["contenu"] + "\n\n"
            
            self.logger.info(f"Contexte trouvé: {len(resultats)} documents avec extension .{extension}")
            return contexte, resultats
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de contexte: {str(e)}")
            return "", []
    
    def add_documents(self, new_documents: List[Document]) -> bool:
        """
        Ajoute de nouveaux documents à la base vectorielle existante.
        
        Args:
            new_documents: Nouveaux documents à ajouter
            
        Returns:
            bool: True si l'ajout a réussi, False sinon
        """
        if not self.vectordb:
            loaded = self.load_vectordb()
            if not loaded:
                self.logger.error("Impossible de charger la base vectorielle pour l'ajout de documents")
                return False
        
        try:
            self.logger.info(f"Ajout de {len(new_documents)} nouveaux documents à la base vectorielle...")
            
            # Découper les documents en chunks
            chunks = self.split_documents(new_documents)
            
            # Ajouter les chunks à la base
            self.vectordb.add_documents(chunks)
            
            self.logger.info(f"Documents ajoutés avec succès.")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout de documents: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur la base vectorielle.
        
        Returns:
            Dictionnaire contenant diverses statistiques
        """
        if not self.vectordb:
            loaded = self.load_vectordb()
            if not loaded:
                return {
                    "status": "not_loaded",
                    "message": "La base vectorielle n'a pas pu être chargée"
                }
        
        try:
            # Récupérer des informations de la base
            collection = self.vectordb._collection
            count = collection.count()
            
            # Analyser les sources des documents
            sources = {}
            extensions = {}
            
            metadatas = collection.get(include=["metadatas"])["metadatas"]
            
            for metadata in metadatas:
                if "source" in metadata:
                    source = metadata["source"]
                    
                    # Compter par source
                    if source in sources:
                        sources[source] += 1
                    else:
                        sources[source] = 1
                    
                    # Compter par extension
                    _, ext = os.path.splitext(source)
                    if ext:
                        if ext in extensions:
                            extensions[ext] += 1
                        else:
                            extensions[ext] = 1
            
            # Top sources et extensions
            top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]
            top_extensions = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "status": "ok",
                "document_count": count,
                "unique_sources": len(sources),
                "extensions": {ext: count for ext, count in top_extensions},
                "top_sources": {os.path.basename(src): count for src, count in top_sources}
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def update_from_directory(self, directory: str, 
                             extensions: Optional[List[str]] = None,
                             recreate: bool = False) -> bool:
        """
        Met à jour la base vectorielle à partir d'un dossier.
        
        Args:
            directory: Chemin du dossier contenant les documents
            extensions: Liste des extensions de fichier à inclure
            recreate: Si True, recrée complètement la base au lieu de la mettre à jour
            
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            self.logger.info(f"Mise à jour de la base vectorielle depuis {directory}...")
            
            # Charger les documents
            documents = self.load_code_documents(directory, extensions)
            
            if recreate:
                # Créer une nouvelle base
                return self.create_vectordb(documents, force_recreate=True)
            else:
                # Ajouter à la base existante
                return self.add_documents(documents)
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour depuis {directory}: {str(e)}")
            return False
    
    def test_search(self, test_queries: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Teste la recherche dans la base vectorielle avec quelques requêtes.
        
        Args:
            test_queries: Liste de requêtes de test (utilise des requêtes par défaut si None)
            
        Returns:
            Dictionnaire des résultats par requête
        """
        if not self.vectordb:
            loaded = self.load_vectordb()
            if not loaded:
                return {}
        
        # Quelques requêtes de test par défaut
        if test_queries is None:
            test_queries = [
                "Comment créer une page de connexion dans Flutter",
                "Comment implémenter une liste déroulante avec recherche",
                "Comment gérer l'authentification avec Firebase",
                "Comment créer une interface adaptative pour différentes tailles d'écran"
            ]
        
        self.logger.info("Test de recherche dans la base vectorielle...")
        
        results = {}
        for query in test_queries:
            self.logger.info(f"Requête: '{query}'")
            
            # Effectuer la recherche
            docs = self.vectordb.similarity_search(query, k=2)
            
            # Formater les résultats
            query_results = []
            for i, doc in enumerate(docs):
                source = doc.metadata.get('source', 'Inconnue')
                content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                
                self.logger.info(f"Résultat {i+1}:")
                self.logger.info(f"Source: {source}")
                self.logger.info(f"Contenu: {content}")
                
                query_results.append({
                    "source": source,
                    "content": content,
                    "full_content": doc.page_content
                })
            
            results[query] = query_results
        
        return results