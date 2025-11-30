from fastapi import APIRouter, HTTPException
from app.models.schemas import VoyageData, PredictionResult, BatchPredictionRequest, BatchPredictionResponse
from app.core.model_loader import model_loader
from typing import Any

router = APIRouter()

@router.post("/predict", response_model=PredictionResult)
async def predict(data: VoyageData) -> Any:
    """
    Make a prediction for a single voyage.
    """
    try:
        result = await model_loader.predict(data)
        return result
    except RuntimeError as e:
        # External API or configuration errors
        raise HTTPException(status_code=503, detail="Prediction service unavailable. Please try again later.")
    except Exception as e:
        # Unexpected errors - log but don't expose details
        import logging
        logging.getLogger(__name__).exception("Unexpected error in prediction")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(batch_data: BatchPredictionRequest) -> Any:
    """
    Make predictions for a batch of voyages.
    """
    try:
        predictions = await model_loader.predict_batch(batch_data.voyages)
        return BatchPredictionResponse(predictions=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Batch prediction service unavailable.")

@router.get("/model/info")
async def model_info():
    """
    Get information about the loaded model.
    """
    from app.core.config import get_settings
    settings = get_settings()
    return {
        "type": "External API",
        "url": settings.EXTERNAL_MODEL_URL
    }
