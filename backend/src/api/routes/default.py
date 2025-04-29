from fastapi import APIRouter

router = APIRouter(
    prefix="",
    tags=["default"],
    responses={404: {"description": "Not found"}},
)

@router.get("/ping", 
    summary="Vérifier l'état de l'API",
    description="Cette route permet de vérifier si l'API est en ligne et fonctionne correctement.",
    response_description="Retourne un message de confirmation que l'API est en ligne",
    responses={
        200: {
            "description": "API en ligne",
            "content": {
                "application/json": {
                    "example": {"message": "pong"}
                }
            }
        }
    }
)
async def ping():
    """
    Vérifie l'état de l'API.
    
    Returns:
        dict: Un dictionnaire contenant un message de confirmation
    """
    return {"message": "pong"} 