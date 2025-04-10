from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """DTO pour la création d'un utilisateur"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """DTO pour la connexion d'un utilisateur"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """DTO pour le token JWT"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """DTO pour les données du token"""
    email: Optional[str] = None

class UserResponse(BaseModel):
    """DTO pour la réponse avec les informations de l'utilisateur"""
    id: str
    username: str
    email: EmailStr
    is_active: bool
    roles: list[str]
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True 