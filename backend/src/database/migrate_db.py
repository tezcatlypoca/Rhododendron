import os
import sys

# Ajout du dossier backend au PYTHONPATH
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

from backend.src.database.migrations.add_projet_id_to_agents import upgrade

def run_migrations():
    print("Démarrage des migrations...")
    try:
        upgrade()
        print("Migration terminée avec succès !")
    except Exception as e:
        print(f"Erreur lors de la migration : {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations() 