from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from ...models.schemas.auth import UserResponse, UserCreate
from ...services.auth_service import AuthService
from ..dependencies import get_auth_service
from ...database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": "Utilisateur non trouvé"},
        400: {"description": "Requête invalide"}
    }
)

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    auth_service: AuthService = Depends(get_auth_service)
):
    """Récupère tous les utilisateurs"""
    try:
        users = await auth_service.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Récupère un utilisateur par son ID"""
    try:
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Met à jour un utilisateur"""
    try:
        user = await auth_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Supprime un utilisateur"""
    try:
        success = await auth_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        return {"message": "Utilisateur supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 