from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..models.domain.user import User
from ..models.schemas.auth import UserCreate, Token, TokenData
from ..core.config import settings
from ..repositories.user_repository import UserRepository

# Configuration de la sécurité
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(self, user_data: UserCreate) -> User:
        """Enregistre un nouvel utilisateur"""
        # Vérifier si l'email existe déjà
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Un utilisateur avec cet email existe déjà")

        # Créer l'utilisateur
        hashed_password = pwd_context.hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )

        # Sauvegarder l'utilisateur
        return await self.user_repository.save(user)

    async def login(self, email: str, password: str) -> Token:
        """Connecte un utilisateur et retourne un token JWT"""
        user = await self.user_repository.get_by_email(email)
        if not user or not pwd_context.verify(password, user._hashed_password):
            raise ValueError("Email ou mot de passe incorrect")

        # Mettre à jour la dernière connexion
        await self.user_repository.update_last_login(user.id)

        # Générer le token JWT
        access_token = self._create_access_token(
            data={"sub": user.email}
        )
        return Token(access_token=access_token)

    async def get_current_user(self, token: str) -> User:
        """Récupère l'utilisateur à partir du token JWT"""
        try:
            payload = self._decode_token(token)
            email: str = payload.get("sub")
            if email is None:
                raise ValueError("Token invalide")
            
            user = await self.user_repository.get_by_email(email)
            if user is None:
                raise ValueError("Utilisateur non trouvé")
            
            return user
        except JWTError:
            raise ValueError("Token invalide")

    def _create_access_token(self, data: dict) -> str:
        """Crée un token JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def _decode_token(self, token: str) -> dict:
        """Décode un token JWT"""
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        ) 