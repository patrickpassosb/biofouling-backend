from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class VoyageData(BaseModel):
    shipName: str = Field(..., description="Name of the ship")
    speed: float = Field(..., description="Speed of the ship")
    duration: float = Field(..., description="Duration of the voyage")
    distance: float = Field(..., description="Distance traveled")
    beaufortScale: int = Field(..., description="Beaufort scale (weather condition)")
    Area_Molhada: float = Field(..., description="Wetted area of the ship")
    MASSA_TOTAL_TON: float = Field(..., description="Total mass in tons")
    TIPO_COMBUSTIVEL_PRINCIPAL: str = Field(..., description="Main fuel type")
    decLatitude: float = Field(..., description="Decimal Latitude")
    decLongitude: float = Field(..., description="Decimal Longitude")
    DiasDesdeUltimaLimpeza: float = Field(..., description="Days since last cleaning")

class PredictionResult(BaseModel):
    ship_id: str
    biofouling_level: int = Field(..., description="Predicted biofouling level (0-3)")
    risk_category: str = Field(..., description="Risk category: Low, Medium, High, Critical")
    recommended_action: str = Field(..., description="Recommended maintenance action")
    estimated_fuel_impact: float = Field(..., description="Estimated % increase in fuel consumption")
    confidence_score: float = Field(..., description="Model confidence score (0-1)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BatchPredictionRequest(BaseModel):
    voyages: List[VoyageData]

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResult]
