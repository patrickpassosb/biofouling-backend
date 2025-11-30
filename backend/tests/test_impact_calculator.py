"""
Testes unitários para ImpactCalculator.

Valida cálculos de impacto de biofouling com dados conhecidos.
"""

import pytest
from app.core.impact_calculator import calculator
from app.core.constants import (
    SFOC_TYPICAL,
    PROPULSIVE_EFFICIENCY_CLEAN,
    BIOFOULING_IMPACT_TABLE
)
from app.models.schemas import VoyageData


def create_test_voyage() -> VoyageData:
    """Cria dados de viagem de teste."""
    return VoyageData(
        shipName="TEST-SHIP",
        speed=15.0,
        duration=10.0,
        distance=3600.0,
        beaufortScale=3,
        Area_Molhada=5000.0,
        MASSA_TOTAL_TON=50000.0,
        TIPO_COMBUSTIVEL_PRINCIPAL="LSHFO",
        decLatitude=-23.0,
        decLongitude=-43.0,
        DiasDesdeUltimaLimpeza=180.0
    )


def test_calculate_base_power():
    """Testa cálculo de potência base."""
    voyage = create_test_voyage()
    power = calculator.calculate_base_power(voyage)
    
    # Validar que potência é positiva e razoável
    assert power > 0
    # Para um navio de 50000 toneladas a 15 nós, esperamos potência significativa
    assert power > 1000  # Mínimo razoável
    assert power < 100000  # Máximo razoável


def test_calculate_fuel_consumption():
    """Testa cálculo de consumo de combustível."""
    power_kw = 10000.0
    duration_hours = 24.0
    sfoc = SFOC_TYPICAL
    
    fuel_tons = calculator.calculate_fuel_consumption(power_kw, duration_hours, sfoc)
    
    # Validar cálculo: FC = P × SFOC × t / 1,000,000
    expected = (power_kw * sfoc * duration_hours) / 1_000_000
    assert abs(fuel_tons - expected) < 0.01
    
    # Validar que consumo é positivo
    assert fuel_tons > 0


@pytest.mark.asyncio
async def test_calculate_impact_level_0():
    """Testa cálculo de impacto para nível 0 (limpo)."""
    voyage = create_test_voyage()
    impact = await calculator.calculate_impact(voyage, biofouling_level=0)
    
    # Nível 0 não deve ter impacto
    assert impact["delta_power_kw"] == 0.0
    assert impact["delta_power_percent"] == 0.0
    assert impact["extra_fuel_tons"] == 0.0
    assert impact["extra_cost_usd"] == 0.0
    assert impact["extra_co2_tons"] == 0.0
    
    # Potências devem ser iguais
    assert impact["base_power_kw"] == impact["fouled_power_kw"]
    assert impact["base_fuel_tons"] == impact["total_fuel_tons"]


@pytest.mark.asyncio
async def test_calculate_impact_level_2():
    """Testa cálculo de impacto para nível 2 (moderado)."""
    voyage = create_test_voyage()
    impact = await calculator.calculate_impact(voyage, biofouling_level=2, fuel_type="LSHFO")
    
    # Validar que há impacto positivo
    assert impact["delta_power_kw"] > 0
    assert impact["delta_power_percent"] > 0
    assert impact["extra_fuel_tons"] > 0
    assert impact["extra_cost_usd"] > 0
    assert impact["extra_co2_tons"] > 0
    
    # Validar que potência fouled é maior que base
    assert impact["fouled_power_kw"] > impact["base_power_kw"]
    
    # Validar que consumo total é maior que base
    assert impact["total_fuel_tons"] > impact["base_fuel_tons"]
    
    # Validar descrição
    assert impact["biofouling_description"] == BIOFOULING_IMPACT_TABLE[2]["description"]
    
    # Validar range de rugosidade
    assert impact["ks_range_um"] == BIOFOULING_IMPACT_TABLE[2]["ks_range_um"]
    
    # Validar que custos BRL são proporcionais a USD
    assert impact["extra_cost_brl"] > 0
    assert impact["total_cost_brl"] > 0
    assert impact["exchange_rate_used"] > 0


@pytest.mark.asyncio
async def test_calculate_impact_level_3():
    """Testa cálculo de impacto para nível 3 (severo)."""
    voyage = create_test_voyage()
    impact = await calculator.calculate_impact(voyage, biofouling_level=3)
    
    # Nível 3 deve ter impacto maior que nível 2
    voyage_level2 = create_test_voyage()
    impact_level2 = await calculator.calculate_impact(voyage_level2, biofouling_level=2)
    
    assert impact["delta_power_percent"] > impact_level2["delta_power_percent"]
    assert impact["extra_fuel_percent"] > impact_level2["extra_fuel_percent"]
    assert impact["extra_cost_usd"] > impact_level2["extra_cost_usd"]


@pytest.mark.asyncio
async def test_calculate_impact_different_fuel_types():
    """Testa cálculo com diferentes tipos de combustível."""
    voyage = create_test_voyage()
    
    impact_lshfo = await calculator.calculate_impact(voyage, biofouling_level=2, fuel_type="LSHFO")
    impact_vlsfo = await calculator.calculate_impact(voyage, biofouling_level=2, fuel_type="VLSFO")
    
    # VLSFO é mais caro, então custo deve ser maior
    assert impact_vlsfo["extra_cost_usd"] > impact_lshfo["extra_cost_usd"]
    
    # Mas consumo de combustível deve ser o mesmo
    assert impact_vlsfo["extra_fuel_tons"] == impact_lshfo["extra_fuel_tons"]


@pytest.mark.asyncio
async def test_calculate_impact_invalid_level():
    """Testa validação de nível de biofouling inválido."""
    voyage = create_test_voyage()
    
    with pytest.raises(ValueError):
        await calculator.calculate_impact(voyage, biofouling_level=-1)
    
    with pytest.raises(ValueError):
        await calculator.calculate_impact(voyage, biofouling_level=4)


@pytest.mark.asyncio
async def test_calculate_impact_cost_calculation():
    """Testa que custos são calculados corretamente."""
    voyage = create_test_voyage()
    impact = await calculator.calculate_impact(voyage, biofouling_level=2, fuel_type="LSHFO")
    
    # Custo total deve ser OPEX + EU ETS
    expected_total_usd = impact["extra_cost_usd"] + impact["eu_ets_cost_usd"]
    assert abs(impact["total_cost_usd"] - expected_total_usd) < 0.01
    
    # Custo total BRL deve ser proporcional
    expected_total_brl = impact["extra_cost_brl"] + impact["eu_ets_cost_brl"]
    assert abs(impact["total_cost_brl"] - expected_total_brl) < 0.01


@pytest.mark.asyncio
async def test_calculate_impact_co2_calculation():
    """Testa que emissões de CO₂ são calculadas corretamente."""
    voyage = create_test_voyage()
    impact = await calculator.calculate_impact(voyage, biofouling_level=2, fuel_type="LSHFO")
    
    # CO₂ deve ser proporcional ao consumo extra de combustível
    # Para LSHFO, fator é 3.114
    from app.core.constants import CO2_CONVERSION_FACTORS
    co2_factor = CO2_CONVERSION_FACTORS["LSHFO"]
    expected_co2 = impact["extra_fuel_tons"] * co2_factor
    
    assert abs(impact["extra_co2_tons"] - expected_co2) < 0.01


def test_normalize_fuel_type():
    """Testa normalização de tipos de combustível."""
    # Tipos conhecidos devem retornar normalizados
    assert calculator._normalize_fuel_type("LSHFO") == "LSHFO"
    assert calculator._normalize_fuel_type("lshfo") == "LSHFO"  # Case insensitive
    assert calculator._normalize_fuel_type("VLSFO") == "VLSFO"
    assert calculator._normalize_fuel_type("MGO") == "MGO"
    
    # Tipos com correspondência parcial devem funcionar
    assert calculator._normalize_fuel_type("LSHFO 0.5") == "LSHFO"  # Deve matchar início
    assert calculator._normalize_fuel_type("ULSMGO 0.1") == "ULSMGO"  # Deve matchar início
    
    # Tipo desconhecido retorna em uppercase para validação posterior
    assert calculator._normalize_fuel_type("UNKNOWN") == "UNKNOWN"
    
    # Validação de entrada
    import pytest
    with pytest.raises(ValueError):
        calculator._normalize_fuel_type("")
    with pytest.raises(ValueError):
        calculator._normalize_fuel_type(None)

