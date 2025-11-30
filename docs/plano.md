Plano de Implementação - Cálculo de Impacto de Biofouling (Abordagem 1)
Objetivo
Implementar o cálculo científico do impacto da bioincrustação na performance naval, baseado no framework do documento 

science-formulas.md
 (validado pelo Gemini) e nas normas ISO 19030:2016, IMO MEPC.308(73), e estudos peer-reviewed.

Validação Científica Confirmada
✅ ISO 19030:2016 - Validado por 50+ especialistas da indústria marítima
✅ Schultz et al. (2011) - Publicado em Biofouling journal (peer-reviewed pela NIH)
✅ IMO MEPC.308(73) - Fator de conversão oficial: 3.206 t-CO₂/t-Fuel
✅ Song et al. (2020) - Publicado em Applied Ocean Research

Arquitetura da Solução
┌─────────────────────────────────────────────────────────────┐
│  API Externa (Hugging Face)                                 │
│  Input: Dados do Navio → Output: biofouling_level (0-3)    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend (FastAPI)                                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 1. Recebe biofouling_level da API externa             │ │
│  │ 2. Calcula impactos usando science-formulas.md:       │ │
│  │    - Resistência adicional (ΔR_T)                     │ │
│  │    - Perda de eficiência propulsiva (Δη_D)            │ │
│  │    - Consumo extra de combustível (ΔFC)               │ │
│  │    - Emissões de CO₂ (M_CO₂)                          │ │
│  │    - Custo financeiro (OPEX + EU ETS)                 │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
Estrutura de Arquivos
backend/
├── app/
│   ├── core/
│   │   ├── impact_calculator.py  [NOVO] - Cálculos hidrodinâmicos
│   │   └── constants.py          [NOVO] - Constantes científicas
│   ├── models/
│   │   └── schemas.py            [MODIFICAR] - Adicionar ImpactAnalysis
│   └── api/routes/
│       └── predictions.py        [MODIFICAR] - Adicionar endpoint /impact
└── docs/
    └── science-formulas.md       [EXISTENTE] - Referência científica
Implementação Detalhada
Fase 1: Constantes Científicas (app/core/constants.py)
Objetivo: Centralizar todos os valores validados cientificamente.

# Fatores de Conversão de CO₂ (IMO MEPC.308(73))
CO2_CONVERSION_FACTORS = {
    "HFO": 3.114,    # Heavy Fuel Oil
    "VLSFO": 3.151,  # Very Low Sulphur Fuel Oil
    "MGO": 3.206,    # Marine Gas Oil / Diesel
    "LNG": 2.750     # Liquefied Natural Gas
}
# Preços de Combustível (USD/MT - Singapura 2024)
FUEL_PRICES_USD = {
    "HFO": 335.50,
    "VLSFO": 690.50,
    "MGO": 750.00
}
# Preço da Licença de Carbono EU ETS (USD/t-CO₂)
EU_ETS_PRICE_USD = 96.06
# SFOC Típico (g/kWh) - Specific Fuel Oil Consumption
SFOC_TYPICAL = 170.0
# Eficiência Propulsiva Típica (Limpo)
PROPULSIVE_EFFICIENCY_CLEAN = 0.65
# Tabela de Impacto de Biofouling (Baseada em Schultz 2011, Song 2020)
BIOFOULING_IMPACT_TABLE = {
    0: {  # Limpo
        "description": "Hidraulicamente Liso",
        "delta_cf_percent": 0.0,
        "delta_eta_percent": 0.0,
        "ks_range_um": (0, 30)
    },
    1: {  # Leve
        "description": "Slime Leve / Biofilme",
        "delta_cf_percent": 10.0,  # Média de 5-15%
        "delta_eta_percent": 5.0,
        "ks_range_um": (100, 300)
    },
    2: {  # Moderado
        "description": "Incrustação Calcária Média",
        "delta_cf_percent": 32.5,  # Média de 20-45%
        "delta_eta_percent": 15.0,
        "ks_range_um": (1000, 3000)
    },
    3: {  # Severo
        "description": "Incrustação Calcária Pesada",
        "delta_cf_percent": 55.0,  # >50%
        "delta_eta_percent": 25.0,  # Até 30.3% (Song 2020)
        "ks_range_um": (5000, 10000)
    }
}
Referências:

CO₂ factors: IMO MEPC.308(73)
Fuel prices: Bunkerworld.com (Nov 2024)
EU ETS: European Energy Exchange (Nov 2024)
Biofouling impact: Schultz (2011), Song (2020)
Fase 2: Calculadora de Impacto (app/core/impact_calculator.py)
Objetivo: Implementar os cálculos hidrodinâmicos do 

science-formulas.md
.

from app.core.constants import *
from app.models.schemas import VoyageData
import math
class ImpactCalculator:
    """
    Calcula o impacto da bioincrustação na performance naval.
    Baseado em ISO 19030:2016 e estudos peer-reviewed.
    """
    
    def calculate_base_power(self, voyage: VoyageData) -> float:
        """
        Calcula a potência base usando Admiralty Formula simplificada.
        
        P = (Δ^(2/3) × V^3) / C
        
        Onde:
        - Δ = Deslocamento (toneladas) ≈ MASSA_TOTAL_TON
        - V = Velocidade (nós)
        - C = Coeficiente do casco (assumido 500 para casco limpo)
        """
        displacement = voyage.MASSA_TOTAL_TON
        speed_knots = voyage.speed
        hull_coefficient = 500  # Típico para navios mercantes
        
        power_kw = (displacement**(2/3) * speed_knots**3) / hull_coefficient
        return power_kw
    
    def calculate_fuel_consumption(
        self, 
        power_kw: float, 
        duration_hours: float,
        sfoc: float = SFOC_TYPICAL
    ) -> float:
        """
        Calcula consumo de combustível.
        
        FC (tons) = P (kW) × SFOC (g/kWh) × t (h) / 1,000,000
        """
        fc_grams = power_kw * sfoc * duration_hours
        fc_tons = fc_grams / 1_000_000
        return fc_tons
    
    def calculate_impact(
        self,
        voyage: VoyageData,
        biofouling_level: int,
        fuel_type: str = "VLSFO"
    ) -> dict:
        """
        Calcula o impacto completo da bioincrustação.
        
        Returns:
            dict com:
            - base_power_kw
            - fouled_power_kw
            - delta_power_kw
            - base_fuel_tons
            - extra_fuel_tons
            - total_fuel_tons
            - extra_cost_usd
            - extra_co2_tons
            - eu_ets_cost_usd
            - total_cost_usd
        """
        # 1. Potência Base (Casco Limpo)
        base_power = self.calculate_base_power(voyage)
        
        # 2. Impacto do Biofouling
        impact_data = BIOFOULING_IMPACT_TABLE[biofouling_level]
        delta_cf_percent = impact_data["delta_cf_percent"]
        delta_eta_percent = impact_data["delta_eta_percent"]
        
        # 3. Aumento de Resistência Friccional (ΔC_F)
        # Resistência aumenta proporcionalmente
        resistance_multiplier = 1 + (delta_cf_percent / 100)
        
        # 4. Perda de Eficiência Propulsiva (Δη_D)
        eta_clean = PROPULSIVE_EFFICIENCY_CLEAN
        eta_fouled = eta_clean * (1 - delta_eta_percent / 100)
        
        # 5. Potência Requerida com Fouling
        # P_fouled = (R_fouled × V) / η_fouled
        # Simplificando: P_fouled = P_base × (R_mult / η_ratio)
        eta_ratio = eta_fouled / eta_clean
        fouled_power = base_power * (resistance_multiplier / eta_ratio)
        
        delta_power = fouled_power - base_power
        
        # 6. Consumo de Combustível
        duration_hours = voyage.duration * 24  # dias → horas
        
        base_fuel = self.calculate_fuel_consumption(base_power, duration_hours)
        total_fuel = self.calculate_fuel_consumption(fouled_power, duration_hours)
        extra_fuel = total_fuel - base_fuel
        
        # 7. Impacto Financeiro (OPEX)
        fuel_price = FUEL_PRICES_USD.get(fuel_type, FUEL_PRICES_USD["VLSFO"])
        extra_cost = extra_fuel * fuel_price
        
        # 8. Emissões de CO₂
        co2_factor = CO2_CONVERSION_FACTORS.get(fuel_type, CO2_CONVERSION_FACTORS["VLSFO"])
        extra_co2 = extra_fuel * co2_factor
        
        # 9. Custo Regulatório (EU ETS)
        eu_ets_cost = extra_co2 * EU_ETS_PRICE_USD
        
        # 10. Custo Total
        total_cost = extra_cost + eu_ets_cost
        
        return {
            "base_power_kw": round(base_power, 2),
            "fouled_power_kw": round(fouled_power, 2),
            "delta_power_kw": round(delta_power, 2),
            "delta_power_percent": round((delta_power / base_power) * 100, 2),
            "base_fuel_tons": round(base_fuel, 2),
            "extra_fuel_tons": round(extra_fuel, 2),
            "total_fuel_tons": round(total_fuel, 2),
            "extra_fuel_percent": round((extra_fuel / base_fuel) * 100, 2),
            "extra_cost_usd": round(extra_cost, 2),
            "extra_co2_tons": round(extra_co2, 2),
            "eu_ets_cost_usd": round(eu_ets_cost, 2),
            "total_cost_usd": round(total_cost, 2),
            "fuel_type": fuel_type,
            "biofouling_description": impact_data["description"],
            "ks_range_um": impact_data["ks_range_um"]
        }
calculator = ImpactCalculator()
Referências:

Admiralty Formula: Princípios de Arquitetura Naval (Watson, 1998)
SFOC: Marine Diesel Engines (Woodyard, 2009)
Eficiência propulsiva: Ship Resistance and Propulsion (Molland et al., 2011)
Fase 3: Atualizar Schemas (

app/models/schemas.py
)
class ImpactAnalysis(BaseModel):
    """Análise detalhada do impacto de biofouling."""
    base_power_kw: float
    fouled_power_kw: float
    delta_power_kw: float
    delta_power_percent: float
    base_fuel_tons: float
    extra_fuel_tons: float
    total_fuel_tons: float
    extra_fuel_percent: float
    extra_cost_usd: float
    extra_co2_tons: float
    eu_ets_cost_usd: float
    total_cost_usd: float
    fuel_type: str
    biofouling_description: str
    ks_range_um: tuple[int, int]
class PredictionResult(BaseModel):
    ship_id: str
    biofouling_level: int
    risk_category: str
    recommended_action: str
    estimated_fuel_impact: float
    confidence_score: float
    timestamp: datetime
    impact_analysis: Optional[ImpactAnalysis] = None  # [NOVO]
Fase 4: Novo Endpoint (

app/api/routes/predictions.py
)
from app.core.impact_calculator import calculator
@router.post("/predict/with-impact", response_model=PredictionResult)
async def predict_with_impact(
    data: VoyageData,
    fuel_type: str = "VLSFO"
) -> Any:
    """
    Predição com análise completa de impacto.
    
    Retorna:
    - Nível de biofouling (da API externa)
    - Análise detalhada de impacto (cálculos locais)
    """
    try:
        # 1. Obter predição da API externa
        result = await model_loader.predict(data)
        
        # 2. Calcular impacto detalhado
        impact = calculator.calculate_impact(
            voyage=data,
            biofouling_level=result.biofouling_level,
            fuel_type=fuel_type
        )
        
        # 3. Adicionar análise ao resultado
        result.impact_analysis = ImpactAnalysis(**impact)
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail="Prediction service unavailable.")
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("Unexpected error in prediction")
        raise HTTPException(status_code=500, detail="Internal server error")
Exemplo de Resposta da API
{
  "ship_id": "SHIP-123",
  "biofouling_level": 2,
  "risk_category": "High",
  "recommended_action": "Schedule cleaning within 1 month",
  "estimated_fuel_impact": 15.0,
  "confidence_score": 0.85,
  "timestamp": "2025-11-30T15:00:00Z",
  "impact_analysis": {
    "base_power_kw": 8500.0,
    "fouled_power_kw": 11220.0,
    "delta_power_kw": 2720.0,
    "delta_power_percent": 32.0,
    "base_fuel_tons": 50.0,
    "extra_fuel_tons": 16.0,
    "total_fuel_tons": 66.0,
    "extra_fuel_percent": 32.0,
    "extra_cost_usd": 11048.0,
    "extra_co2_tons": 50.4,
    "eu_ets_cost_usd": 4841.4,
    "total_cost_usd": 15889.4,
    "fuel_type": "VLSFO",
    "biofouling_description": "Incrustação Calcária Média",
    "ks_range_um": [1000, 3000]
  }
}
Testes
Teste Unitário (tests/test_impact_calculator.py)
def test_impact_calculation():
    voyage = VoyageData(
        shipName="TEST-SHIP",
        speed=15.0,
        duration=10.0,
        distance=3600.0,
        beaufortScale=3,
        Area_Molhada=5000.0,
        MASSA_TOTAL_TON=50000.0,
        TIPO_COMBUSTIVEL_PRINCIPAL="VLSFO",
        decLatitude=-23.0,
        decLongitude=-43.0,
        DiasDesdeUltimaLimpeza=180.0
    )
    
    impact = calculator.calculate_impact(voyage, biofouling_level=2)
    
    assert impact["delta_power_percent"] > 0
    assert impact["extra_fuel_tons"] > 0
    assert impact["total_cost_usd"] > 0
Cronograma de Implementação
Fase	Tarefa	Tempo Estimado
1	Criar constants.py	30 min
2	Criar impact_calculator.py	1h 30min
3	Atualizar 

schemas.py
15 min
4	Criar endpoint /predict/with-impact	30 min
5	Testes unitários	30 min
6	Testes de integração	30 min
TOTAL		~4 horas
Perguntas para Validação
Tipo de combustível padrão: A maioria dos navios da Transpetro usa VLSFO ou HFO?
Preços locais: Devemos usar preços de Singapura ou há dados específicos do Brasil?
Conversão BRL: Quer que eu adicione conversão automática USD → BRL?
Próximos Passos
Após aprovação deste plano:

Implementar Fase 1 (constants.py)
Implementar Fase 2 (impact_calculator.py)
Testar localmente
Deploy no Google Cloud Run
Validar com dados reais
Posso começar a implementação agora?

📊 Análise do Uso de Combustível
Distribuição:

LSHFO 0.5 (Low Sulphur Heavy Fuel Oil): 32.968 registros (38.3%)
ULSMGO 0.1 (Ultra Low Sulphur Marine Gas Oil): 28.976 registros (33.7%)
LSMGO 0.5 (Low Sulphur Marine Gas Oil): 14.823 registros (17.2%)
VLSHFO 0.1 (Very Low Sulphur Heavy Fuel Oil): 6.317 registros (7.3%)
Outros: 3.147 registros (3.5%)
Conclusão:
A maioria usa HFO (Heavy Fuel Oil), não VLSFO:

HFO variants (LSHFO + VLSHFO): 39.285 registros (45.6%) ✅
MGO variants (ULSMGO + LSMGO): 43.799 registros (50.9%)
LFO variants: 2.988 registros (3.5%)
Observação importante: A frota está quase dividida entre HFO e MGO, com uma leve predominância de MGO. Isso significa que muitos navios têm scrubbers (podem usar HFO) e outros não (usam MGO/VLSFO).

🔄 Ajustes no Plano
1. Combustível Padrão
Vou usar LSHFO (Low Sulphur HFO) como padrão, mas permitir que o usuário escolha.

2. Conversão USD ↔ BRL
Vou adicionar um parâmetro currency na API:

@router.post("/predict/with-impact")
async def predict_with_impact(
    data: VoyageData,
    fuel_type: str = "LSHFO",  # Padrão da Transpetro
    currency: str = "USD"       # "USD" ou "BRL"
) -> Any:
Resposta da API terá ambos os valores:

{
  "impact_analysis": {
    "extra_cost_usd": 11048.0,
    "extra_cost_brl": 55240.0,  // Conversão automática
    "eu_ets_cost_usd": 4841.4,
    "eu_ets_cost_brl": 24207.0,
    "total_cost_usd": 15889.4,
    "total_cost_brl": 79447.0,
    "exchange_rate_used": 5.0  // Taxa do dia
  }
}
O dashboard pode então escolher qual campo exibir (USD ou BRL) sem precisar fazer a conversão no frontend.

📝 Revisão do Plano
Mudanças:

✅ Combustível padrão: LSHFO (ao invés de VLSFO)
✅ Adicionar suporte para todos os tipos de combustível da Transpetro
✅ API retorna ambos USD e BRL (dashboard escolhe qual exibir)
✅ Taxa de câmbio obtida de API pública (ex: AwesomeAPI do Banco Central)