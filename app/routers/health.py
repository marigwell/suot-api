from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def get_health():
    return {
        "status": "healthy",
        "service": "Suot API",
        "version": "0.1.0"
        }