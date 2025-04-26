import os
import sys
import signal
from contextlib import asynccontextmanager

# Ajout du dossier backend au PYTHONPATH
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from src.api.routes import auth, agent_routes, conversation_routes, user_routes, websocket_routes
from src.core.config import settings
from src.database import init_db, get_db
from sqlalchemy import create_engine
from src.database.models import Base
from src.services.agent_manager import AgentManager
from src.services.agent_service import AgentService
from sqlalchemy.orm import Session
import asyncio

# Variable globale pour suivre l'état de l'application
app = None

def signal_handler(signum, frame):
    """Gère les signaux d'arrêt"""
    print("\nArrêt de l'application en cours...")
    if app:
        # Ici vous pouvez ajouter du code de nettoyage si nécessaire
        print("Nettoyage terminé.")
    sys.exit(0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application"""
    # Configuration des handlers de signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialisation de la base de données
    init_db()
    
    # Démarrer l'AgentManager
    agent_manager = AgentManager()
    await agent_manager.start()
    
    # Enregistrer les agents existants
    agent_service = AgentService()
    db = next(get_db())
    try:
        agents = agent_service.get_all_agents(db)
        for agent in agents:
            await agent_manager.register_agent(
                agent_id=agent.id,
                role=agent.role,
                initial_context={
                    "model_type": agent.model_type,
                    "config": agent.config
                }
            )
    finally:
        db.close()
    
    yield
    
    # Code de nettoyage à l'arrêt
    print("Arrêt de l'application...")

# Vérification de l'existence de la base de données
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents.db")
if not os.path.exists(db_path):
    print("Initialisation de la base de données...")
    engine = create_engine('sqlite:///agents.db')
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès !")

# Création de l'application FastAPI
app = FastAPI(
    title="API Rhododendron",
    description="API pour le projet Rhododendron",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation de la base de données
@app.on_event("startup")
async def startup_event():
    init_db()
    
    # Démarrer l'AgentManager
    agent_manager = AgentManager()
    await agent_manager.start()
    
    # Enregistrer les agents existants
    agent_service = AgentService()
    db = next(get_db())
    try:
        agents = agent_service.get_all_agents(db)
        for agent in agents:
            await agent_manager.register_agent(
                agent_id=agent.id,
                role=agent.role,
                initial_context={
                    "model_type": agent.model_type,
                    "config": agent.config
                }
            )
    finally:
        db.close()

# Enregistrement des routers
app.include_router(auth.router, tags=["auth"])
app.include_router(agent_routes.router, tags=["agents"])
app.include_router(conversation_routes.router, tags=["conversations"])
app.include_router(user_routes.router, tags=["users"])
app.include_router(websocket_routes.router, tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Rhododendron"}

@app.get("/doc", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description="""
        API Rhododendron - Documentation complète

        ## Routes d'authentification
        - Gestion des utilisateurs et des sessions
        - `POST /auth/register` : Créer un nouveau compte
        - `POST /auth/login` : Se connecter
        - `GET /auth/me` : Récupérer les informations de l'utilisateur connecté

        ## Routes des utilisateurs
        - Gestion des utilisateurs
        - `GET /users/` : Lister tous les utilisateurs
        - `GET /users/{id}` : Récupérer un utilisateur spécifique
        - `PUT /users/{id}` : Mettre à jour un utilisateur
        - `DELETE /users/{id}` : Supprimer un utilisateur

        ## Routes des agents
        - Création et gestion des agents IA
        - Traitement des requêtes par les agents
        - Configuration et personnalisation des agents

        ### Endpoints disponibles :
        - `POST /agents/` : Créer un nouvel agent
        - `GET /agents/` : Lister tous les agents
        - `GET /agents/{id}` : Récupérer un agent spécifique
        - `PUT /agents/{id}` : Mettre à jour un agent
        - `POST /agents/{id}/request` : Envoyer une requête à un agent

        ## Routes des conversations
        - Gestion des conversations avec les agents
        - `POST /conversations/` : Créer une nouvelle conversation
        - `GET /conversations/` : Lister toutes les conversations
        - `GET /conversations/{id}` : Récupérer une conversation spécifique
        - `PUT /conversations/{id}` : Mettre à jour une conversation
        - `DELETE /conversations/{id}` : Supprimer une conversation
        - `DELETE /conversations/` : Supprimer toutes les conversations
        - `POST /conversations/{conversation_id}/messages` : Ajouter un message à une conversation
        - `GET /conversations/{conversation_id}/messages` : Récupérer les messages d'une conversation
        - `PUT /conversations/{conversation_id}/title` : Mettre à jour le titre d'une conversation
        - `PUT /conversations/{conversation_id}/agent` : Mettre à jour l'agent d'une conversation
        """,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi 

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\nArrêt de l'application...")
        sys.exit(0) 