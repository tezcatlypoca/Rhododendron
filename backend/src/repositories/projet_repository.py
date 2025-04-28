from sqlalchemy.orm import Session
from ..database.models import Projet
from ..models.dto.projet_dto import ProjetCreate, ProjetUpdate
from typing import List, Optional

class ProjetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, projet: ProjetCreate, compte_id: int) -> Projet:
        db_projet = Projet(
            nom=projet.nom,
            description=projet.description,
            compte_id=compte_id
        )
        self.db.add(db_projet)
        self.db.commit()
        self.db.refresh(db_projet)
        return db_projet

    def get_by_id(self, projet_id: int) -> Optional[Projet]:
        return self.db.query(Projet).filter(Projet.id == projet_id).first()

    def get_by_compte(self, compte_id: int) -> List[Projet]:
        return self.db.query(Projet).filter(Projet.compte_id == compte_id).all()

    def update(self, projet_id: int, projet: ProjetUpdate) -> Optional[Projet]:
        db_projet = self.get_by_id(projet_id)
        if db_projet:
            for key, value in projet.dict(exclude_unset=True).items():
                setattr(db_projet, key, value)
            self.db.commit()
            self.db.refresh(db_projet)
        return db_projet

    def delete(self, projet_id: int) -> bool:
        db_projet = self.get_by_id(projet_id)
        if db_projet:
            self.db.delete(db_projet)
            self.db.commit()
            return True
        return False 