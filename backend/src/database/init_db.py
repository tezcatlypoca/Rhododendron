import os
from sqlalchemy import create_engine
from .models import Base

def init_db():
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "agents.db")
    
    # Création du moteur de base de données
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Création de toutes les tables
    Base.metadata.create_all(bind=engine)
    
    print("Base de données initialisée avec succès !")

if __name__ == "__main__":
    init_db() 