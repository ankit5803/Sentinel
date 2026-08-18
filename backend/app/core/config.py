from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# This dynamically finds the 'Sentinel' root directory by going up 4 levels from config.py
# __file__ (config.py) -> core -> app -> backend -> Sentinel
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    """
    Centralized configuration for Sentinel.
    Reads values from a .env file locally, or from system environment variables in production.
    """
    ENVIRONMENT: str = "local"
    DEBUG: bool = False
    
    # Database and Cache (Dummy defaults so the app runs before we configure Postgres/Redis)
    DATABASE_URL: str = "postgresql://user:password@localhost/sentinel"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Model Artifact Paths (Dynamically resolved based on project root)
    ENGLISH_MODEL_PATH: str = str(PROJECT_ROOT / "ml" / "training" / "artifacts" / "english_distilbert")
    HINGLISH_MODEL_PATH: str = str(PROJECT_ROOT / "ml" / "training" / "artifacts" / "hinglish_distilbert")

    # Pydantic v2 specific settings dict
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Caches the settings so the .env file is only parsed once during startup.
    This prevents unnecessary file I/O reads on every single API request.
    """
    return Settings()

# --- Quick Test ---
if __name__ == "__main__":
    settings = get_settings()
    print("✅ Config loaded successfully!")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Resolved English Model Path: {settings.ENGLISH_MODEL_PATH}")