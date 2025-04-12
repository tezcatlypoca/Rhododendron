from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.domain.user import User
from ..database import User as UserModel

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email"""
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None
        return User(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            roles=user.roles.split(",") if user.roles else [],
            created_at=user.created_at,
            last_login=user.last_login
        )

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Récupère un utilisateur par son ID"""
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None
        return User(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            roles=user.roles.split(",") if user.roles else [],
            created_at=user.created_at,
            last_login=user.last_login
        )

    async def get_all(self) -> List[User]:
        """Récupère tous les utilisateurs"""
        users = self.db.query(UserModel).all()
        return [
            User(
                id=user.id,
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                roles=user.roles.split(",") if user.roles else [],
                created_at=user.created_at,
                last_login=user.last_login
            )
            for user in users
        ]

    async def save(self, user: User) -> User:
        """Sauvegarde un utilisateur"""
        user_model = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user._hashed_password,
            is_active=user.is_active,
            roles=",".join(user.roles),
            created_at=user.created_at,
            last_login=user.last_login
        )
        self.db.add(user_model)
        self.db.commit()
        self.db.refresh(user_model)
        return user

    async def update_last_login(self, user_id: str) -> None:
        """Met à jour la date de dernière connexion"""
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user.last_login = datetime.now()
            self.db.commit()

    async def delete(self, user_id: str) -> bool:
        """Supprime un utilisateur"""
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True 