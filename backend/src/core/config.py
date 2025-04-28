from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Settings(BaseSettings):
    # Configuration de l'application
    APP_NAME: str = "Rhododendron"
    DEBUG: bool = False
    
    # Configuration de la sécurité
    SECRET_KEY: str = "votre_clé_secrète_très_longue_et_complexe"  # À changer en production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuration de la base de données
    DATABASE_URL: str = "sqlite:///agents.db"

    class Config:
        env_file = ".env"

# Instance des paramètres
settings = Settings() 