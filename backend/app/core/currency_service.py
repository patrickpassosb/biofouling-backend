"""
Serviço para obter taxa de câmbio USD/BRL.

Usa API pública com cache para evitar muitas requisições.
Fallback para taxa fixa se API indisponível.
"""

import httpx
import time
import logging
from app.core.constants import FALLBACK_USD_BRL_RATE

logger = logging.getLogger(__name__)

class CurrencyService:
    """
    Serviço para obter taxa de câmbio USD/BRL.
    
    Implementa cache de 1 hora para evitar muitas requisições à API.
    """
    
    def __init__(self):
        self._cached_rate: float | None = None
        self._cache_timestamp: float | None = None
        self._cache_duration: int = 3600  # 1 hora em segundos
        self._api_url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
    
    async def get_usd_brl_rate(self) -> float:
        """
        Obtém taxa de câmbio USD/BRL.
        
        Retorna:
            Taxa de câmbio (ex: 5.0 significa 1 USD = 5.0 BRL)
        
        Usa cache de 1 hora. Se API falhar, retorna taxa fallback.
        """
        # Verificar cache
        if self._cached_rate is not None and self._cache_timestamp is not None:
            elapsed = time.time() - self._cache_timestamp
            if elapsed < self._cache_duration:
                logger.debug(f"Using cached USD/BRL rate: {self._cached_rate}")
                return self._cached_rate
        
        # Buscar nova taxa da API
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self._api_url)
                response.raise_for_status()
                data = response.json()
                
                # AwesomeAPI retorna {"USDBRL": {"bid": "5.1234", ...}}
                if "USDBRL" in data:
                    rate_str = data["USDBRL"].get("bid")
                    if rate_str:
                        rate = float(rate_str)
                        self._cached_rate = rate
                        self._cache_timestamp = time.time()
                        logger.info(f"Fetched new USD/BRL rate: {rate}")
                        return rate
                
                logger.warning("API response format unexpected, using fallback")
                return FALLBACK_USD_BRL_RATE
                
        except httpx.TimeoutException:
            logger.warning("Timeout fetching USD/BRL rate, using fallback")
            return FALLBACK_USD_BRL_RATE
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error fetching USD/BRL rate: {e.response.status_code}, using fallback")
            return FALLBACK_USD_BRL_RATE
        except Exception as e:
            logger.error(f"Error fetching USD/BRL rate: {e}, using fallback")
            return FALLBACK_USD_BRL_RATE
    
    def convert_usd_to_brl(self, usd_amount: float, rate: float | None = None) -> float:
        """
        Converte valor de USD para BRL.
        
        Args:
            usd_amount: Valor em USD
            rate: Taxa de câmbio (opcional, se None usa taxa atual)
        
        Returns:
            Valor em BRL
        """
        if rate is None:
            # Se não forneceu taxa, usar fallback (não pode fazer async aqui)
            rate = FALLBACK_USD_BRL_RATE
        
        return round(usd_amount * rate, 2)

# Instância singleton do serviço
currency_service = CurrencyService()
