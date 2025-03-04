import unittest
import os
import sys
import time  # Ajout de l'import manquant
from pathlib import Path
import tempfile
import shutil

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_manager import RAGManager
from src.document_loader import DocumentLoaderUI
from settings import PATH_CONFIG

class TestRhododendronSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialisation des ressources pour tous les tests"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_config = {
            "base": cls.temp_dir,
            "data": os.path.join(cls.temp_dir, "data"),
            "projets": os.path.join(cls.temp_dir, "projets"),
            "documentation": os.path.join(cls.temp_dir, "documentation"),
            "vector_db": os.path.join(cls.temp_dir, "vector_db"),
            "generated_prompt": os.path.join(cls.temp_dir, "generated")
        }
        
        # Créer les dossiers nécessaires
        for path in cls.test_config.values():
            os.makedirs(path, exist_ok=True)
            
        # Créer quelques fichiers de test
        cls.create_test_files()

    @classmethod
    def tearDownClass(cls):
        """Nettoyage après tous les tests"""
        try:
            # Fermer explicitement la connexion à la base vectorielle
            if hasattr(cls, 'rag_manager'):
                if cls.rag_manager.vectordb:
                    cls.rag_manager.vectordb._client.close()
                    
            # Attendre un peu pour s'assurer que les connexions sont fermées
            time.sleep(1)
            
            # Supprimer le dossier temporaire
            shutil.rmtree(cls.temp_dir)
        except PermissionError as e:
            print(f"Warning: Impossible de supprimer certains fichiers: {e}")

    @classmethod
    def create_test_files(cls):
        """Crée des fichiers de test"""
        # Fichier Flutter
        flutter_content = """
        class LoginPage extends StatelessWidget {
          @override
          Widget build(BuildContext context) {
            return Scaffold(
              body: Center(
                child: Text('Login Page'),
              ),
            );
          }
        }
        """
        with open(os.path.join(cls.test_config["projets"], "login_page.dart"), "w") as f:
            f.write(flutter_content)

        # Fichier Java
        java_content = """
        public class MainActivity extends AppCompatActivity {
            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);
            }
        }
        """
        with open(os.path.join(cls.test_config["projets"], "MainActivity.java"), "w") as f:
            f.write(java_content)

    def setUp(self):
        """Initialisation avant chaque test"""
        # Utiliser un dossier unique pour chaque test
        test_dir = os.path.join(self.test_config["vector_db"], f"test_{time.time()}")
        self.rag_manager = RAGManager(
            vector_db_dir=test_dir,
            data_dir=self.test_config["data"]
        )

    def test_1_document_loading(self):
        """Test le chargement des documents"""
        docs = self.rag_manager.load_code_documents(
            self.test_config["projets"],
            extensions=["dart", "java"]
        )
        self.assertTrue(len(docs) > 0, "Aucun document chargé")
        self.assertEqual(len(docs), 2, "Nombre incorrect de documents chargés")

    def test_2_vectordb_creation(self):
        """Test la création de la base vectorielle"""
        docs = self.rag_manager.load_code_documents(self.test_config["projets"])
        success = self.rag_manager.create_vectordb(docs, force_recreate=True)
        self.assertTrue(success, "Échec de la création de la base vectorielle")

    def test_3_search_functionality(self):
        """Test la fonctionnalité de recherche"""
        # Assurer que la base existe
        if not self.rag_manager.vectordb:
            docs = self.rag_manager.load_code_documents(self.test_config["projets"])
            self.rag_manager.create_vectordb(docs)

        # Test de recherche
        query = "login page flutter"
        context, results = self.rag_manager.search_context(query, k=2)
        
        self.assertTrue(len(results) > 0, "Aucun résultat trouvé")
        self.assertTrue(any("login" in r["contenu"].lower() for r in results))

    def test_4_extension_filtering(self):
        """Test le filtrage par extension"""
        # Test pour les fichiers Dart
        context, results = self.rag_manager.filter_by_extension("dart", "widget", k=1)
        self.assertTrue(all(r["source"].endswith(".dart") for r in results))

        # Test pour les fichiers Java
        context, results = self.rag_manager.filter_by_extension("java", "activity", k=1)
        self.assertTrue(all(r["source"].endswith(".java") for r in results))

    def test_5_statistics(self):
        """Test la génération des statistiques"""
        # Recréer une base propre pour ce test
        self.rag_manager = RAGManager(
            vector_db_dir=os.path.join(self.test_config["vector_db"], "stats_test"),
            data_dir=self.test_config["data"]
        )
        
        # Charger uniquement les fichiers initiaux
        docs = self.rag_manager.load_code_documents(
            self.test_config["projets"],
            extensions=["dart", "java"]
        )
        success = self.rag_manager.create_vectordb(docs, force_recreate=True)
        self.assertTrue(success)
        
        # Vérifier les statistiques
        stats = self.rag_manager.get_statistics()
        
        self.assertEqual(stats["status"], "ok")
        self.assertTrue("document_count" in stats)
        self.assertTrue("extensions" in stats)
        self.assertEqual(stats["document_count"], 2)

    def test_6_update_functionality(self):
        """Test la fonctionnalité de mise à jour"""
        # Ajouter un nouveau fichier
        new_file_path = os.path.join(self.test_config["projets"], "new_page.dart")
        with open(new_file_path, "w") as f:
            f.write("class NewPage extends StatelessWidget {}")

        # Mettre à jour la base
        success = self.rag_manager.update_from_directory(
            self.test_config["projets"],
            extensions=["dart"],
            recreate=False
        )
        
        self.assertTrue(success, "Échec de la mise à jour")
        
        # Vérifier que le nouveau fichier est trouvable
        context, results = self.rag_manager.search_context("NewPage")
        self.assertTrue(any("NewPage" in r["contenu"] for r in results))

if __name__ == '__main__':
    unittest.main(verbosity=2)