import os
import sys

# Ajout du dossier backend au PYTHONPATH
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_path)

from backend.src.database.init_db import init_db

def reset_database():
    print("Réinitialisation de la base de données...")
    try:
        # Suppression de l'ancienne base de données si elle existe
        db_path = os.path.join(backend_path, "agents.db")
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Ancienne base de données supprimée.")
        
        # Initialisation de la nouvelle base de données
        init_db()
        print("Base de données réinitialisée avec succès !")
    except Exception as e:
        print(f"Erreur lors de la réinitialisation : {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database() 