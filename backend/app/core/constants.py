"""
Constantes científicas para cálculo de impacto de biofouling.

Baseado em:
- ISO 19030:2016
- IMO MEPC.308(73)
- Schultz et al. (2011)
- Song et al. (2020)
"""

# Fatores de Conversão de CO₂ (IMO MEPC.308(73))
# Unidade: t-CO₂ / t-fuel
CO2_CONVERSION_FACTORS = {
    "HFO": 3.114,      # Heavy Fuel Oil
    "HSFO": 3.114,     # High Sulphur Fuel Oil (mesmo que HFO)
    "LSHFO": 3.114,    # Low Sulphur Heavy Fuel Oil
    "VLSFO": 3.151,    # Very Low Sulphur Fuel Oil
    "VLSHFO": 3.151,   # Very Low Sulphur Heavy Fuel Oil
    "MGO": 3.206,      # Marine Gas Oil / Diesel
    "LSMGO": 3.206,    # Low Sulphur Marine Gas Oil
    "ULSMGO": 3.206,   # Ultra Low Sulphur Marine Gas Oil
    "LNG": 2.750       # Liquefied Natural Gas
}

# Preços de Combustível (USD/MT - Singapura 2024)
# Fonte: Bunkerworld.com (Nov 2024)
FUEL_PRICES_USD = {
    "HFO": 335.50,
    "HSFO": 335.50,
    "LSHFO": 335.50,   # Low Sulphur HFO (assumido mesmo preço que HFO)
    "VLSFO": 690.50,
    "VLSHFO": 690.50,  # Very Low Sulphur HFO (assumido mesmo preço que VLSFO)
    "MGO": 750.00,
    "LSMGO": 750.00,   # Low Sulphur MGO (assumido mesmo preço que MGO)
    "ULSMGO": 750.00   # Ultra Low Sulphur MGO (assumido mesmo preço que MGO)
}

# Preço da Licença de Carbono EU ETS (USD/t-CO₂)
# Fonte: European Energy Exchange (Nov 2024)
EU_ETS_PRICE_USD = 96.06

# SFOC Típico (g/kWh) - Specific Fuel Oil Consumption
# Padrão da indústria marítima
SFOC_TYPICAL = 170.0

# Eficiência Propulsiva Típica (Limpo)
# Range típico: 0.60 - 0.70 para navios mercantes
PROPULSIVE_EFFICIENCY_CLEAN = 0.65

# Tabela de Impacto de Biofouling
# Baseada em Schultz (2011) e Song (2020)
# Valores representam médias dos ranges encontrados na literatura
BIOFOULING_IMPACT_TABLE = {
    0: {  # Limpo
        "description": "Hidraulicamente Liso",
        "delta_cf_percent": 0.0,      # Aumento no coeficiente de resistência friccional
        "delta_eta_percent": 0.0,     # Perda de eficiência propulsiva
        "ks_range_um": (0, 30)        # Rugosidade equivalente (micrômetros)
    },
    1: {  # Leve
        "description": "Slime Leve / Biofilme",
        "delta_cf_percent": 10.0,     # Média de 5-15%
        "delta_eta_percent": 5.0,
        "ks_range_um": (100, 300)
    },
    2: {  # Moderado
        "description": "Incrustação Calcária Média",
        "delta_cf_percent": 32.5,     # Média de 20-45%
        "delta_eta_percent": 15.0,
        "ks_range_um": (1000, 3000)
    },
    3: {  # Severo
        "description": "Incrustação Calcária Pesada",
        "delta_cf_percent": 55.0,     # >50%
        "delta_eta_percent": 25.0,    # Até 30.3% (Song 2020)
        "ks_range_um": (5000, 10000)
    }
}

# Coeficiente do Casco para Admiralty Formula
# Típico para navios mercantes
HULL_COEFFICIENT = 500

# Taxa de Câmbio Fallback USD/BRL
# Usada quando API de câmbio não está disponível
FALLBACK_USD_BRL_RATE = 5.0

# Lista oficial de tipos de combustível suportados (baseado na análise da Transpetro)
VALID_FUEL_TYPES = frozenset([
    "HFO", "HSFO", "LSHFO", "VLSFO", "VLSHFO",
    "MGO", "LSMGO", "ULSMGO", "LNG"
])
