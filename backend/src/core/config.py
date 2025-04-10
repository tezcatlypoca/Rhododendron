from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Settings(BaseSettings):
    # Configuration de l'application
    APP_NAME: str = "Rhododendron"
    DEBUG: bool = True
    
    # Configuration de la sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY", "votre_clé_secrète_très_longue_et_complexe")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Configuration de la base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./users.db")

    class Config:
        env_file = ".env"

# Instance des paramètres
settings = Settings() 