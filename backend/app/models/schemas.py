from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class VoyageData(BaseModel):
    ship_id: str = Field(..., description="Unique identifier for the ship")
    voyage_duration_days: float = Field(..., gt=0, description="Duration of the voyage in days")
    avg_speed: float = Field(..., gt=0, description="Average speed in knots")
    distance_traveled: float = Field(..., gt=0, description="Total distance traveled in nautical miles")
    port_time_ratio: float = Field(..., ge=0, le=1, description="Ratio of time spent in port (0-1)")
    fuel_consumption: float = Field(..., gt=0, description="Total fuel consumption in tons")
    temperature_avg: float = Field(..., description="Average sea water temperature in Celsius")
    last_cleaning_days: int = Field(..., ge=0, description="Days since last hull cleaning")

class PredictionResult(BaseModel):
    ship_id: str
    biofouling_level: int = Field(..., description="Predicted biofouling level (0-3)")
    risk_category: str = Field(..., description="Risk category: Low, Medium, High, Critical")
    recommended_action: str = Field(..., description="Recommended maintenance action")
    estimated_fuel_impact: float = Field(..., description="Estimated % increase in fuel consumption")
    confidence_score: float = Field(..., description="Model confidence score (0-1)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BatchPredictionRequest(BaseModel):
    voyages: List[VoyageData]

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResult]
