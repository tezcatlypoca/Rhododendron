from sqlalchemy.orm import Session
from fastapi import Depends

from ..repositories.user_repository import UserRepository
from ..services.auth_service import AuthService
from ..database import get_db

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Crée une instance du repository des utilisateurs"""
    return UserRepository(db)

def get_auth_service(user_repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    """Crée une instance du service d'authentification"""
    return AuthService(user_repository) 