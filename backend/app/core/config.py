# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentinel API"
    
    # The Postgres Database URL (Defaulting to our local Docker setup)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sentinel")
    
    # MLflow Tracking Server Location
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    # Load dynamically from the MLflow Model Registry using the '@production' alias
    ENGLISH_MODEL_URI: str = os.getenv("ENGLISH_MODEL_URI", "models:/Sentinel-English-Model@production")
    HINGLISH_MODEL_URI: str = os.getenv("HINGLISH_MODEL_URI", "models:/Sentinel-Hinglish-Model@production")

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()