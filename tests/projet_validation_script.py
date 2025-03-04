import os
import sys
import shutil
import logging
import subprocess

# Ajouter le chemin du projet au PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Importer à partir de la racine du projet
from settings import PATH_CONFIG
from src.rag_manager import RAGManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('project_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ProjectValidation')

class ProjectValidator:
    def __init__(self):
        # Chemins de configuration
        self.base_dir = PATH_CONFIG['base']
        self.data_dir = PATH_CONFIG['data']
        self.projets_dir = PATH_CONFIG['projets']
        self.doc_dir = PATH_CONFIG['documentation']
        self.vectordb_dir = PATH_CONFIG['vector_db']
        
        # Création des dossiers s'ils n'existent pas
        self.create_directories()
    
    def create_directories(self):
        """Crée les répertoires nécessaires s'ils n'existent pas"""
        dirs_to_create = [
            self.base_dir, 
            self.data_dir, 
            self.projets_dir, 
            self.doc_dir, 
            self.vectordb_dir
        ]
        
        for directory in dirs_to_create:
            os.makedirs(directory, exist_ok=True)
    
    def check_dependencies(self):
        """Vérifie les dépendances du projet"""
        logger.info("🔍 Vérification des dépendances")
        required_packages = [
            'langchain', 'transformers', 'torch', 'sentence-transformers', 
            'streamlit', 'ollama', 'chroma', 'huggingface_hub'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✅ {package} installé")
            except ImportError:
                logger.warning(f"❌ {package} manquant")
                missing_packages.append(package)
        
        if missing_packages:
            logger.warning("Packages manquants. Installation recommandée.")
            return False
        return True
    
    def test_document_loader(self):
        """Test du chargement de documents"""
        logger.info("🧪 Test du chargement de documents")
        try:
            from src.document_loader import DocumentLoaderUI
            logger.info("✅ Module de chargement de documents importé avec succès")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur de chargement du module: {e}")
            return False
    
    def create_test_project(self):
        """Crée un projet de test"""
        logger.info("🚧 Création d'un projet de test")
        test_project_path = os.path.join(self.projets_dir, 'test_project')
        
        # Créer un projet Flutter minimal
        os.makedirs(test_project_path, exist_ok=True)
        
        # Créer quelques fichiers de test
        test_files = [
            ('lib/main.dart', '''
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Test Project',
      home: HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Test Project')),
      body: Center(child: Text('Hello, World!')),
    );
  }
}
'''),
            ('pubspec.yaml', '''
name: test_project
description: A test Flutter project

environment:
  sdk: '>=2.12.0 <3.0.0'

dependencies:
  flutter:
    sdk: flutter
'''),
            ('README.md', '# Test Project\n\nThis is a minimal test project')
        ]
        
        for filepath, content in test_files:
            full_path = os.path.join(test_project_path, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        logger.info("✅ Projet de test créé avec succès")
        return test_project_path
    
    def test_rag_manager(self, test_project_path):
        """Test complet du RAG Manager"""
        logger.info("🧪 Test du RAG Manager")
        
        try:
            # Initialiser le RAG Manager
            rag_manager = RAGManager(
                vector_db_dir=self.vectordb_dir,
                data_dir=self.data_dir
            )
            
            # Charger les documents de code
            code_docs = rag_manager.load_code_documents(test_project_path)
            logger.info(f"✅ Chargé {len(code_docs)} documents de code")
            
            # Découper les documents
            chunks = rag_manager.split_documents(code_docs)
            logger.info(f"✅ Découpé en {len(chunks)} chunks")
            
            # Créer la base vectorielle
            success = rag_manager.create_vectordb(chunks, force_recreate=True)
            if not success:
                logger.error("❌ Échec de création de la base vectorielle")
                return False
            
            # Tester la recherche
            query = "Comment créer une application Flutter simple"
            contexte, resultats = rag_manager.search_context(query, k=3)
            
            logger.info(f"✅ Recherche effectuée. {len(resultats)} résultats trouvés")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Erreur lors du test du RAG Manager: {e}")
            return False
    
    def test_streamlit_app(self):
        """Vérification de la configuration de l'application Streamlit"""
        logger.info("🧪 Vérification de l'application Streamlit")
        try:
             # Méthode 1 : Importer directement
            from app_with_rag_manager import main
        
            # Méthode 2 : Importer avec le chemin complet
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            from app_with_rag_manager import main
        
            logger.info("✅ Application Streamlit importée avec succès")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur d'import de l'application Streamlit: {e}")
            return False
    
    def run_full_validation(self):
        """Exécute la validation complète du projet"""
        logger.info("🚀 Validation complète du projet Rhododendron")
        
        # Vérification des dépendances
        dependencies_ok = self.check_dependencies()
        
        # Test du document loader
        document_loader_ok = self.test_document_loader()
        
        # Créer un projet de test
        test_project_path = self.create_test_project()
        
        # Test du RAG Manager
        rag_manager_ok = self.test_rag_manager(test_project_path)
        
        # Test de l'application Streamlit
        streamlit_app_ok = self.test_streamlit_app()
        
        # Rapport final
        logger.info("\n=== RAPPORT FINAL ===")
        logger.info(f"Dépendances: {'✅ OK' if dependencies_ok else '❌ ÉCHEC'}")
        logger.info(f"Chargement de documents: {'✅ OK' if document_loader_ok else '❌ ÉCHEC'}")
        logger.info(f"RAG Manager: {'✅ OK' if rag_manager_ok else '❌ ÉCHEC'}")
        logger.info(f"Application Streamlit: {'✅ OK' if streamlit_app_ok else '❌ ÉCHEC'}")
        
        # Résultat global
        global_result = all([
            dependencies_ok, 
            document_loader_ok, 
            rag_manager_ok, 
            streamlit_app_ok
        ])
        
        return global_result

def main():
    validator = ProjectValidator()
    result = validator.run_full_validation()
    
    if result:
        print("🎉 Validation du projet réussie!")
        sys.exit(0)
    else:
        print("❌ Échec de la validation du projet.")
        sys.exit(1)

if __name__ == "__main__":
    main()