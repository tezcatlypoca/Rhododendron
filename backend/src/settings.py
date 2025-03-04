import yaml, os
from dotenv import load_dotenv

# Charger les variables depuis .env
load_dotenv()

# Accéder aux variables
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "True") == "True"
MODEL_NAME = "codellama:7b-instruct-q4_0"

DB_CONFIG = {
    "type": os.getenv("DB_TYPE", "sqlite"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", ""),
    "name": os.getenv("DB_NAME", "crew_ai"),
}

with open("config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)

print(CONFIG["app"]["name"])  # Crew AI Locale
print(CONFIG["database"]["type"])  # sqlite
print(f"🚀 Lancement en mode {APP_ENV} avec debug={DEBUG}")
