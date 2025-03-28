from typing import List
from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Areum Activity Recognition Service"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    SHOW_DOCS: bool = True
    ALLOWED_ORIGINS: List[AnyHttpUrl] = []
    ML_MODEL_PATH: str = "app/models/trained/activity_model.joblib"

    # Threshold settings for activity detection
    ACTIVITY_DETECTION_THRESHOLD: float = 0.3
    MOVEMENT_CONSISTENCY_THRESHOLD: float = 0.5

    # API keys for external services (if needed)
    ANALYTICS_ENGINE_API_KEY: str = ""
    ANALYTICS_ENGINE_URL: str = "http://data-analytics-engine:8000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
