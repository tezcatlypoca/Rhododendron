from functools import lru_cache

from ..repositories.user_repository import UserRepository
from ..services.auth_service import AuthService

@lru_cache()
def get_user_repository() -> UserRepository:
    """Crée une instance du repository des utilisateurs"""
    return UserRepository()

@lru_cache()
def get_auth_service() -> AuthService:
    """Crée une instance du service d'authentification"""
    return AuthService(get_user_repository()) 