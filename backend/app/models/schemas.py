from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
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

class ImpactAnalysis(BaseModel):
    """Análise detalhada do impacto de biofouling."""
    base_power_kw: float = Field(..., description="Potência base (casco limpo) em kW")
    fouled_power_kw: float = Field(..., description="Potência com biofouling em kW")
    delta_power_kw: float = Field(..., description="Aumento de potência em kW")
    delta_power_percent: float = Field(..., description="Percentual de aumento de potência")
    base_fuel_tons: float = Field(..., description="Consumo base de combustível em toneladas")
    extra_fuel_tons: float = Field(..., description="Consumo extra devido ao biofouling em toneladas")
    total_fuel_tons: float = Field(..., description="Consumo total de combustível em toneladas")
    extra_fuel_percent: float = Field(..., description="Percentual de aumento no consumo")
    extra_cost_usd: float = Field(..., description="Custo adicional em USD")
    extra_cost_brl: float = Field(..., description="Custo adicional em BRL")
    extra_co2_tons: float = Field(..., description="Emissões extras de CO₂ em toneladas")
    eu_ets_cost_usd: float = Field(..., description="Custo EU ETS em USD")
    eu_ets_cost_brl: float = Field(..., description="Custo EU ETS em BRL")
    total_cost_usd: float = Field(..., description="Custo total em USD")
    total_cost_brl: float = Field(..., description="Custo total em BRL")
    fuel_type: str = Field(..., description="Tipo de combustível usado")
    biofouling_description: str = Field(..., description="Descrição do nível de biofouling")
    ks_range_um: Tuple[int, int] = Field(..., description="Faixa de rugosidade equivalente em μm")
    exchange_rate_used: float = Field(..., description="Taxa de câmbio USD/BRL usada")
    preferred_currency: str = Field(..., description="Moeda preferida para exibição (USD ou BRL)")

class PredictionResult(BaseModel):
    ship_id: str
    biofouling_level: int = Field(..., description="Predicted biofouling level (0-3)")
    risk_category: str = Field(..., description="Risk category: Low, Medium, High, Critical")
    recommended_action: str = Field(..., description="Recommended maintenance action")
    estimated_fuel_impact: float = Field(..., description="Estimated % increase in fuel consumption")
    confidence_score: float = Field(..., description="Model confidence score (0-1)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    impact_analysis: Optional[ImpactAnalysis] = Field(None, description="Análise detalhada de impacto (opcional)")

class BatchPredictionRequest(BaseModel):
    voyages: List[VoyageData]

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResult]
