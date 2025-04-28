"""
Package routes - Contient les routeurs FastAPI
"""
from .projet_routes import router as projet_router
from .auth import router as auth_router
from .agent_routes import router as agent_router
from .conversation_routes import router as conversation_router
from .user_routes import router as user_router
from .websocket_routes import router as websocket_router

__all__ = [
    'projet_router',
    'auth_router',
    'agent_router',
    'conversation_router',
    'user_router',
    'websocket_router'
]