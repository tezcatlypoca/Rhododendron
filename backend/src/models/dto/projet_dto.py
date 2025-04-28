from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProjetBase(BaseModel):
    nom: str
    description: Optional[str] = None

class ProjetCreate(ProjetBase):
    pass

class ProjetUpdate(ProjetBase):
    pass

class ProjetInDB(ProjetBase):
    id: int
    date_creation: datetime
    date_modification: datetime
    compte_id: int

    class Config:
        from_attributes = True 