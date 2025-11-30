"""
Calculadora de impacto de biofouling na performance naval.

Baseado em:
- ISO 19030:2016
- IMO MEPC.308(73)
- Schultz et al. (2011)
- Song et al. (2020)
"""

from app.core.constants import (
    CO2_CONVERSION_FACTORS,
    FUEL_PRICES_USD,
    EU_ETS_PRICE_USD,
    SFOC_TYPICAL,
    PROPULSIVE_EFFICIENCY_CLEAN,
    BIOFOULING_IMPACT_TABLE,
    HULL_COEFFICIENT,
    VALID_FUEL_TYPES
)
from app.core.currency_service import currency_service
from app.models.schemas import VoyageData
import logging

logger = logging.getLogger(__name__)


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
        
        Args:
            voyage: Dados da viagem
        
        Returns:
            Potência em kW
        
        Raises:
            ValueError: Se valores de entrada forem inválidos (≤ 0)
        """
        displacement = voyage.MASSA_TOTAL_TON
        speed_knots = voyage.speed
        
        # Validação científica: valores devem ser positivos
        if displacement <= 0:
            raise ValueError(f"MASSA_TOTAL_TON must be positive, got {displacement}")
        if speed_knots <= 0:
            raise ValueError(f"speed must be positive, got {speed_knots}")
        
        hull_coefficient = HULL_COEFFICIENT
        
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
        
        Args:
            power_kw: Potência em kW
            duration_hours: Duração em horas
            sfoc: Specific Fuel Oil Consumption em g/kWh
        
        Returns:
            Consumo de combustível em toneladas
        
        Raises:
            ValueError: Se valores de entrada forem inválidos (≤ 0)
        """
        # Validação científica: valores devem ser positivos
        if power_kw <= 0:
            raise ValueError(f"power_kw must be positive, got {power_kw}")
        if duration_hours <= 0:
            raise ValueError(f"duration_hours must be positive, got {duration_hours}")
        if sfoc <= 0:
            raise ValueError(f"sfoc must be positive, got {sfoc}")
        
        fc_grams = power_kw * sfoc * duration_hours
        fc_tons = fc_grams / 1_000_000
        return fc_tons
    
    async def calculate_impact(
        self,
        voyage: VoyageData,
        biofouling_level: int,
        fuel_type: str = "LSHFO"
    ) -> dict:
        """
        Calcula o impacto completo da bioincrustação.
        
        Args:
            voyage: Dados da viagem
            biofouling_level: Nível de biofouling (0-3)
            fuel_type: Tipo de combustível (padrão: LSHFO)
        
        Returns:
            dict com métricas de impacto:
            - base_power_kw: Potência base (casco limpo)
            - fouled_power_kw: Potência com fouling
            - delta_power_kw: Aumento de potência
            - delta_power_percent: Aumento percentual de potência
            - base_fuel_tons: Consumo base de combustível
            - extra_fuel_tons: Consumo extra devido ao fouling
            - total_fuel_tons: Consumo total
            - extra_fuel_percent: Aumento percentual de combustível
            - extra_cost_usd: Custo extra em USD
            - extra_cost_brl: Custo extra em BRL
            - extra_co2_tons: Emissões extras de CO₂
            - eu_ets_cost_usd: Custo EU ETS em USD
            - eu_ets_cost_brl: Custo EU ETS em BRL
            - total_cost_usd: Custo total em USD
            - total_cost_brl: Custo total em BRL
            - fuel_type: Tipo de combustível usado
            - biofouling_description: Descrição do nível de biofouling
            - ks_range_um: Range de rugosidade equivalente
            - exchange_rate_used: Taxa de câmbio usada
        """
        # Validar biofouling_level
        if biofouling_level < 0 or biofouling_level > 3:
            raise ValueError(f"biofouling_level must be between 0 and 3, got {biofouling_level}")
        
        # Validar tipo de combustível
        fuel_type_normalized = self._normalize_fuel_type(fuel_type)
        if fuel_type_normalized not in VALID_FUEL_TYPES:
            raise ValueError(f"Invalid fuel_type '{fuel_type}'. Valid types: {sorted(VALID_FUEL_TYPES)}")
        
        # Validar dados da viagem
        if voyage.duration <= 0:
            raise ValueError(f"duration must be positive, got {voyage.duration}")
        
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
        fuel_price = FUEL_PRICES_USD.get(
            fuel_type_normalized, 
            FUEL_PRICES_USD.get("LSHFO", 335.50)
        )
        extra_cost_usd = extra_fuel * fuel_price
        
        # 8. Emissões de CO₂
        co2_factor = CO2_CONVERSION_FACTORS.get(
            fuel_type_normalized,
            CO2_CONVERSION_FACTORS.get("LSHFO", 3.114)
        )
        extra_co2 = extra_fuel * co2_factor
        
        # 9. Custo Regulatório (EU ETS)
        eu_ets_cost_usd = extra_co2 * EU_ETS_PRICE_USD
        
        # 10. Custo Total (USD)
        total_cost_usd = extra_cost_usd + eu_ets_cost_usd
        
        # 11. Conversão para BRL
        exchange_rate = await currency_service.get_usd_brl_rate()
        extra_cost_brl = currency_service.convert_usd_to_brl(extra_cost_usd, exchange_rate)
        eu_ets_cost_brl = currency_service.convert_usd_to_brl(eu_ets_cost_usd, exchange_rate)
        total_cost_brl = currency_service.convert_usd_to_brl(total_cost_usd, exchange_rate)
        
        return {
            "base_power_kw": round(base_power, 2),
            "fouled_power_kw": round(fouled_power, 2),
            "delta_power_kw": round(delta_power, 2),
            "delta_power_percent": round((delta_power / base_power) * 100, 2) if base_power > 0 else 0.0,
            "base_fuel_tons": round(base_fuel, 2),
            "extra_fuel_tons": round(extra_fuel, 2),
            "total_fuel_tons": round(total_fuel, 2),
            "extra_fuel_percent": round((extra_fuel / base_fuel) * 100, 2) if base_fuel > 0 else 0.0,
            "extra_cost_usd": round(extra_cost_usd, 2),
            "extra_cost_brl": round(extra_cost_brl, 2),
            "extra_co2_tons": round(extra_co2, 2),
            "eu_ets_cost_usd": round(eu_ets_cost_usd, 2),
            "eu_ets_cost_brl": round(eu_ets_cost_brl, 2),
            "total_cost_usd": round(total_cost_usd, 2),
            "total_cost_brl": round(total_cost_brl, 2),
            "fuel_type": fuel_type_normalized,
            "biofouling_description": impact_data["description"],
            "ks_range_um": impact_data["ks_range_um"],
            "exchange_rate_used": round(exchange_rate, 4),
            "preferred_currency": "USD"  # Será sobrescrito pelo endpoint se necessário
        }
    
    def _normalize_fuel_type(self, fuel_type: str) -> str:
        """
        Normaliza o tipo de combustível para um dos tipos suportados.
        
        Usa correspondência exata primeiro, depois correspondência parcial mais específica
        para evitar matches incorretos (ex: "FO" não deve matchar "VLSFO").
        
        Args:
            fuel_type: Tipo de combustível (pode ser variação)
        
        Returns:
            Tipo normalizado
        """
        if not fuel_type or not isinstance(fuel_type, str):
            raise ValueError(f"fuel_type must be a non-empty string, got {type(fuel_type)}")
        
        fuel_type_upper = fuel_type.upper().strip()
        
        if not fuel_type_upper:
            raise ValueError("fuel_type cannot be empty")
        
        # Mapeamento de variações para tipos normalizados
        # Ordenado do mais específico para o menos específico
        fuel_mapping = {
            "ULSMGO": "ULSMGO",  # Mais específico primeiro
            "VLSHFO": "VLSHFO",
            "LSMGO": "LSMGO",
            "LSHFO": "LSHFO",
            "VLSFO": "VLSFO",
            "HSFO": "HSFO",
            "MGO": "MGO",
            "HFO": "HFO",
            "LNG": "LNG"
        }
        
        # Tentar encontrar correspondência exata primeiro
        if fuel_type_upper in fuel_mapping:
            return fuel_mapping[fuel_type_upper]
        
        # Tentar correspondência parcial, mas apenas se o tipo completo estiver contido
        # Evita matches incorretos como "FO" em "VLSFO"
        for key, value in fuel_mapping.items():
            # Match apenas se o tipo completo estiver no início ou fim da string
            # ou se for exatamente igual (já verificado acima)
            if fuel_type_upper.startswith(key) or fuel_type_upper.endswith(key):
                return value
        
        # Se não encontrou match, retornar o tipo em uppercase para validação posterior
        # Isso permite que a validação em calculate_impact dê erro mais claro
        return fuel_type_upper


# Instância singleton do calculador
calculator = ImpactCalculator()
