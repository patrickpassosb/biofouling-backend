from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import VoyageData, PredictionResult, BatchPredictionRequest, BatchPredictionResponse, ImpactAnalysis
from app.core.model_loader import model_loader
from app.core.impact_calculator import calculator
from typing import Any
import logging

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
        logger = logging.getLogger(__name__)
        logger.exception("Unexpected error in prediction")
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

@router.post("/predict/with-impact", response_model=PredictionResult)
async def predict_with_impact(
    data: VoyageData,
    fuel_type: str = Query("LSHFO", description="Tipo de combustível (LSHFO, ULSMGO, LSMGO, VLSHFO, etc.)"),
    currency: str = Query("USD", description="Moeda preferida para exibição (USD ou BRL) - ambos são retornados sempre")
) -> Any:
    """
    Predição com análise completa de impacto.
    
    Retorna:
    - Nível de biofouling (da API externa)
    - Análise detalhada de impacto (cálculos locais baseados em fórmulas científicas)
    
    A análise inclui:
    - Impacto na potência e consumo de combustível
    - Emissões de CO₂
    - Custos operacionais (OPEX) e regulatórios (EU ETS)
    - Valores em USD e BRL
    
    O parâmetro currency indica a moeda preferida para exibição no frontend,
    mas ambos os valores (USD e BRL) são sempre retornados.
    """
    # Validar currency
    currency_upper = currency.upper().strip()
    if currency_upper not in ("USD", "BRL"):
        raise HTTPException(
            status_code=400,
            detail=f"currency must be 'USD' or 'BRL', got '{currency}'"
        )
    
    try:
        # 1. Obter predição da API externa
        result = await model_loader.predict(data)
        
        # 2. Calcular impacto detalhado
        impact = await calculator.calculate_impact(
            voyage=data,
            biofouling_level=result.biofouling_level,
            fuel_type=fuel_type
        )
        
        # 3. Adicionar campo preferred_currency para o frontend
        impact["preferred_currency"] = currency_upper
        
        # 4. Adicionar análise ao resultado
        result.impact_analysis = ImpactAnalysis(**impact)
        
        return result
    except ValueError as e:
        # Erro de validação (ex: biofouling_level inválido)
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # External API errors
        raise HTTPException(status_code=503, detail="Prediction service unavailable.")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.exception("Unexpected error in prediction with impact")
        raise HTTPException(status_code=500, detail="Internal server error")

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
