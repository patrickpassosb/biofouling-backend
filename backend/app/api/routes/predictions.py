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
        result = model_loader.predict(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(batch_data: BatchPredictionRequest) -> Any:
    """
    Make predictions for a batch of voyages.
    """
    try:
        predictions = model_loader.predict_batch(batch_data.voyages)
        return BatchPredictionResponse(predictions=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@router.get("/model/info")
async def model_info():
    """
    Get information about the loaded model.
    """
    if model_loader.model is None:
        try:
            model_loader.load_model()
        except Exception:
            return {"status": "model not loaded"}
            
    return {
        "type": type(model_loader.model).__name__,
        "pipeline_steps": [step[0] for step in model_loader.model.steps] if hasattr(model_loader.model, 'steps') else "unknown"
    }
