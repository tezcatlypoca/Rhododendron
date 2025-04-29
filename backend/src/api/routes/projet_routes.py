from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ...database import get_db
from ...models.dto.projet_dto import ProjetCreate, ProjetUpdate, ProjetInDB
from ...repositories.projet_repository import ProjetRepository
from ...core.auth import get_current_user

router = APIRouter(
    prefix="/projets",
    tags=["projets"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ProjetInDB)
def create_projet(
    projet: ProjetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Créer un nouveau projet.
    
    - **nom**: Nom du projet (obligatoire)
    - **description**: Description du projet (optionnel)
    """
    repo = ProjetRepository(db)
    return repo.create(projet, current_user.id)

@router.get("/", response_model=List[ProjetInDB])
def get_projets(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer tous les projets de l'utilisateur connecté.
    """
    repo = ProjetRepository(db)
    return repo.get_by_compte(current_user.id)

@router.get("/{projet_id}", response_model=ProjetInDB)
def get_projet(
    projet_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer un projet spécifique par son ID.
    """
    repo = ProjetRepository(db)
    projet = repo.get_by_id(projet_id)
    if not projet or projet.compte_id != current_user.id:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return projet

@router.put("/{projet_id}", response_model=ProjetInDB)
def update_projet(
    projet_id: UUID,
    projet: ProjetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mettre à jour un projet existant.
    
    - **nom**: Nouveau nom du projet (optionnel)
    - **description**: Nouvelle description du projet (optionnel)
    """
    repo = ProjetRepository(db)
    db_projet = repo.get_by_id(projet_id)
    if not db_projet or db_projet.compte_id != current_user.id:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return repo.update(projet_id, projet)

@router.delete("/{projet_id}")
def delete_projet(
    projet_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Supprimer un projet.
    """
    repo = ProjetRepository(db)
    db_projet = repo.get_by_id(projet_id)
    if not db_projet or db_projet.compte_id != current_user.id:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    if repo.delete(projet_id):
        return {"message": "Projet supprimé avec succès"}
    raise HTTPException(status_code=500, detail="Erreur lors de la suppression du projet") 