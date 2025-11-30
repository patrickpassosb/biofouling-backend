from fastapi import APIRouter
from app.core.model_loader import model_loader

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify service status and model availability.
    """
    model_status = "loaded" if model_loader.model is not None else "not_loaded"
    return {
        "status": "healthy",
        "model_status": model_status,
        "service": "biofouling-prediction-api"
    }
