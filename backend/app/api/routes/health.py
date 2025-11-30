from fastapi import APIRouter
from app.core.model_loader import model_loader

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    # For external API, we can consider it "loaded" if the URL is configured
    model_status = "configured" 
    return {"status": "healthy", "model_status": model_status, "service": "biofouling-prediction-api"}
