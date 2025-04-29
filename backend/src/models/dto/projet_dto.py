from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class ProjetBase(BaseModel):
    nom: str
    description: Optional[str] = None

class ProjetCreate(ProjetBase):
    pass

class ProjetUpdate(ProjetBase):
    pass

class ProjetInDB(ProjetBase):
    id: UUID
    date_creation: datetime
    date_modification: datetime
    compte_id: UUID

    class Config:
        from_attributes = True 