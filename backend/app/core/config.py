from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Biofouling Prediction API"
    LOG_LEVEL: str = "INFO"
    
    # External Model Config
    EXTERNAL_MODEL_URL: str = "https://carpenterbb-api-transpetro-hackathon.hf.space/predict"
    EXTERNAL_MODEL_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra='ignore')

@lru_cache()
def get_settings():
    return Settings()
