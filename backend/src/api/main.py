from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import conversation_routes, agent_routes, user_routes, auth, websocket_routes
from .config import settings

app = FastAPI(
    title="API Rhododendron",
    description="""
    API pour le projet Rhododendron, un système de gestion de conversations avec des agents IA.
    
    ## Conversations
    
    Les conversations sont le cœur du système. Chaque conversation peut être associée à un agent IA
    qui répondra aux messages de l'utilisateur.
    
    ### Endpoints disponibles :
    
    - `POST /conversations/` : Crée une nouvelle conversation
    - `GET /conversations/` : Récupère toutes les conversations
    - `GET /conversations/{conversation_id}` : Récupère une conversation spécifique
    - `PUT /conversations/{conversation_id}` : Met à jour une conversation
    - `DELETE /conversations/{conversation_id}` : Supprime une conversation
    - `POST /conversations/{conversation_id}/messages` : Ajoute un message à une conversation
    - `PUT /conversations/{conversation_id}/messages` : Supprime tous les messages d'une conversation
    - `GET /conversations/{conversation_id}/messages` : Récupère les messages d'une conversation
    - `PUT /conversations/{conversation_id}/agent` : Met à jour l'agent d'une conversation
    - `PUT /conversations/{conversation_id}/title` : Met à jour le titre d'une conversation
    
    ## Agents
    
    Les agents sont des entités IA qui peuvent répondre aux messages des utilisateurs.
    
    ### Endpoints disponibles :
    
    - `POST /agents/` : Crée un nouvel agent
    - `GET /agents/` : Récupère tous les agents
    - `GET /agents/{agent_id}` : Récupère un agent spécifique
    - `PUT /agents/{agent_id}` : Met à jour un agent
    - `DELETE /agents/{agent_id}` : Supprime un agent
    - `POST /agents/{agent_id}/request` : Envoie une requête à un agent
    
    ## Utilisateurs
    
    Les utilisateurs sont les personnes qui interagissent avec le système.
    
    ### Endpoints disponibles :
    
    - `POST /users/` : Crée un nouvel utilisateur
    - `GET /users/` : Récupère tous les utilisateurs
    - `GET /users/{user_id}` : Récupère un utilisateur spécifique
    - `PUT /users/{user_id}` : Met à jour un utilisateur
    - `DELETE /users/{user_id}` : Supprime un utilisateur
    
    ## WebSockets
    
    Communication en temps réel pour les conversations.
    
    ### Endpoints disponibles :
    
    - `WS /ws` : Endpoint WebSocket pour la communication en temps réel avec les conversations
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(auth.router, tags=["auth"])
app.include_router(conversation_routes.router)
app.include_router(agent_routes.router)
app.include_router(user_routes.router)
app.include_router(websocket_routes.router, tags=["websockets"])

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Rhododendron"}