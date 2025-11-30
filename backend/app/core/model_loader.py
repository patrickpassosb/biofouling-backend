import joblib
import pandas as pd
import numpy as np
from app.core.config import get_settings
from app.models.schemas import VoyageData, PredictionResult
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load_model(self):
        """Loads the model from the file system."""
        if self.model is None:
            try:
                logger.info(f"Loading model from {settings.MODEL_PATH}...")
                self.model = joblib.load(settings.MODEL_PATH)
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise RuntimeError(f"Could not load model: {e}")

    def predict(self, data: VoyageData) -> PredictionResult:
        """Makes a prediction for a single voyage data entry."""
        if self.model is None:
            self.load_model()

        # Convert input to DataFrame
        input_df = pd.DataFrame([data.model_dump()])
        
        # Ensure columns match training features
        features = [
            "voyage_duration_days",
            "avg_speed",
            "distance_traveled",
            "port_time_ratio",
            "fuel_consumption",
            "temperature_avg",
            "last_cleaning_days"
        ]
        input_data = input_df[features]

        # Predict
        try:
            prediction = self.model.predict(input_data)[0]
            probabilities = self.model.predict_proba(input_data)[0]
            confidence = float(np.max(probabilities))
            
            # Map prediction to risk category and action
            risk_map = {
                0: ("Low", "Routine monitoring", 0.0),
                1: ("Medium", "Schedule inspection within 3 months", 5.0),
                2: ("High", "Schedule cleaning within 1 month", 15.0),
                3: ("Critical", "Immediate cleaning required", 30.0)
            }
            
            risk_category, action, fuel_impact = risk_map.get(int(prediction), ("Unknown", "Check manually", 0.0))

            return PredictionResult(
                ship_id=data.ship_id,
                biofouling_level=int(prediction),
                risk_category=risk_category,
                recommended_action=action,
                estimated_fuel_impact=fuel_impact,
                confidence_score=confidence
            )
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise e

    def predict_batch(self, data_list: list[VoyageData]) -> list[PredictionResult]:
        """Makes predictions for a batch of voyage data entries efficiently."""
        if self.model is None:
            self.load_model()

        if not data_list:
            return []

        # Convert list of objects to DataFrame once
        input_df = pd.DataFrame([d.model_dump() for d in data_list])
        
        # Ensure columns match training features
        features = [
            "voyage_duration_days",
            "avg_speed",
            "distance_traveled",
            "port_time_ratio",
            "fuel_consumption",
            "temperature_avg",
            "last_cleaning_days"
        ]
        input_data = input_df[features]

        try:
            # Vectorized prediction
            predictions = self.model.predict(input_data)
            probabilities = self.model.predict_proba(input_data)
            
            results = []
            risk_map = {
                0: ("Low", "Routine monitoring", 0.0),
                1: ("Medium", "Schedule inspection within 3 months", 5.0),
                2: ("High", "Schedule cleaning within 1 month", 15.0),
                3: ("Critical", "Immediate cleaning required", 30.0)
            }

            for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                confidence = float(np.max(prob))
                risk_category, action, fuel_impact = risk_map.get(int(pred), ("Unknown", "Check manually", 0.0))
                
                results.append(PredictionResult(
                    ship_id=data_list[i].ship_id,
                    biofouling_level=int(pred),
                    risk_category=risk_category,
                    recommended_action=action,
                    estimated_fuel_impact=fuel_impact,
                    confidence_score=confidence
                ))
            
            return results
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            raise e

model_loader = ModelLoader()
