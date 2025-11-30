import httpx
from app.core.config import get_settings
from app.models.schemas import VoyageData, PredictionResult
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load_model(self) -> None:
        """
        No-op for external API integration. 
        We can check connection here if needed.
        """
        logger.info(f"Using external model at {settings.EXTERNAL_MODEL_URL}")

    async def predict(self, data: VoyageData) -> PredictionResult:
        """Sends a prediction request to the external API."""
        
        if not settings.EXTERNAL_MODEL_API_KEY:
            logger.error("EXTERNAL_MODEL_API_KEY is not set.")
            raise RuntimeError("API Key configuration error.")

        payload = data.model_dump()
        headers = {
            "access_token": settings.EXTERNAL_MODEL_API_KEY
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    settings.EXTERNAL_MODEL_URL,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result_data = response.json()
                logger.info(f"External API response: {result_data}")

                # Validate response format
                if not isinstance(result_data, dict):
                     raise ValueError(f"Unexpected response format: {type(result_data)}")

                # Safe access with validation
                prediction_value = result_data.get("prediction")
                if prediction_value is None:
                     # Fallback or error? For now, logging warning and defaulting to 0 if missing
                     logger.warning(f"Response missing 'prediction' field: {result_data}")
                     prediction_value = 0
                
                confidence = result_data.get("confidence", 0.0)

                # Map prediction to risk category and action
                risk_map = {
                    0: ("Low", "Routine monitoring", 0.0),
                    1: ("Medium", "Schedule inspection within 3 months", 5.0),
                    2: ("High", "Schedule cleaning within 1 month", 15.0),
                    3: ("Critical", "Immediate cleaning required", 30.0)
                }
                
                # Safe type conversion
                try:
                    level = int(prediction_value)
                except (ValueError, TypeError):
                    logger.error(f"Invalid prediction value type: {prediction_value}")
                    level = 0  # Default to safe value
                
                risk_category, action, fuel_impact = risk_map.get(level, ("Unknown", "Check manually", 0.0))

                return PredictionResult(
                    ship_id=data.shipName, # Mapping shipName to ship_id
                    biofouling_level=int(prediction_value),
                    risk_category=risk_category,
                    recommended_action=action,
                    estimated_fuel_impact=fuel_impact,
                    confidence_score=confidence
                )

            except httpx.HTTPStatusError as e:
                logger.error(f"External API error: {e.response.text}")
                # Raise a generic error to the upper layer to avoid leaking details to client
                raise RuntimeError(f"External API failed with status {e.response.status_code}")
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                raise e

    async def predict_batch(self, data_list: list[VoyageData]) -> list[PredictionResult]:
        """
        Makes predictions for a batch of voyage data entries efficiently.
        Uses asyncio.gather to send requests in parallel.
        """
        import asyncio
        
        # Create a list of coroutines
        tasks = [self.predict(data) for data in data_list]
        
        # Execute all tasks in parallel
        # return_exceptions=True ensures one failure doesn't crash the whole batch
        results_or_exceptions = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results_or_exceptions:
            if isinstance(result, Exception):
                logger.error(f"Batch item failed: {result}")
                # Optionally handle failure (e.g., append None or a specific error object)
                # For now, we skip failed items to ensure the response is valid
                continue
            valid_results.append(result)
            
        return valid_results

model_loader = ModelLoader()
