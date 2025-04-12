import os
import sys

# Ajout du dossier backend au PYTHONPATH
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from src.api.routes import auth, agent_routes
from src.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url=None,  # Désactive la documentation par défaut
    redoc_url=None,  # Désactive ReDoc par défaut
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(auth.router)
app.include_router(agent_routes.router)

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
        """,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi 