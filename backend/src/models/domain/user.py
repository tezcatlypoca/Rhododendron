from datetime import datetime
from typing import List, Optional
from uuid import uuid4

class User:
    def __init__(
        self,
        username: str,
        email: str,
        hashed_password: str,
        id: Optional[str] = None,
        is_active: bool = True,
        roles: List[str] = None,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        self.id = id or str(uuid4())
        self.username = username
        self.email = email
        self._hashed_password = hashed_password
        self.is_active = is_active
        self.roles = roles or []
        self.created_at = created_at or datetime.now()
        self.last_login = last_login

    def verify_password(self, password: str) -> bool:
        """Vérifie si le mot de passe fourni correspond au hash stocké"""
        # TODO: Implémenter la vérification du mot de passe
        return True

    def update_last_login(self) -> None:
        """Met à jour la date de dernière connexion"""
        self.last_login = datetime.now()

    def add_role(self, role: str) -> None:
        """Ajoute un rôle à l'utilisateur"""
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role: str) -> None:
        """Supprime un rôle de l'utilisateur"""
        if role in self.roles:
            self.roles.remove(role)

    def has_role(self, role: str) -> bool:
        """Vérifie si l'utilisateur a un rôle spécifique"""
        return role in self.roles

    def to_dict(self) -> dict:
        """Convertit l'utilisateur en dictionnaire"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "roles": self.roles,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Crée une instance d'User à partir d'un dictionnaire"""
        return cls(
            id=data.get("id"),
            username=data["username"],
            email=data["email"],
            hashed_password=data["hashed_password"],
            is_active=data.get("is_active", True),
            roles=data.get("roles", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None
        ) 