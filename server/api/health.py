from fastapi import APIRouter
from ..config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {"status": "UP", "app": settings.APP_NAME, "env": settings.ENV}
