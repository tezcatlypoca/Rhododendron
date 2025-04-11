from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

class Agent:
    def __init__(
        self,
        name: str,
        model_type: str,
        id: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        last_used: Optional[datetime] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.id = id or str(uuid4())
        self.name = name
        self.model_type = model_type
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.last_used = last_used
        self.config = config or {}

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête et retourne la réponse"""
        # TODO: Implémenter la logique de traitement avec le modèle
        self.last_used = datetime.now()
        return {
            "status": "success",
            "response": "Réponse du modèle",
            "timestamp": self.last_used.isoformat()
        }

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Met à jour la configuration de l'agent"""
        self.config.update(new_config)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'agent en dictionnaire"""
        return {
            "id": self.id,
            "name": self.name,
            "model_type": self.model_type,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "config": self.config
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Crée une instance d'Agent à partir d'un dictionnaire"""
        return cls(
            id=data.get("id"),
            name=data["name"],
            model_type=data["model_type"],
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
            config=data.get("config", {})
        ) 