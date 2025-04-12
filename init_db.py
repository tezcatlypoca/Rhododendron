import os
from sqlalchemy import create_engine
from backend.src.database.models import Base

def init_database():
    # Supprimer le fichier de base de données existant s'il existe
    if os.path.exists('agents.db'):
        os.remove('agents.db')
    
    # Créer une nouvelle base de données
    engine = create_engine('sqlite:///agents.db')
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès !")

if __name__ == "__main__":
    init_database() 