import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5439/career_copilot"
    REDIS_URL: str = "redis://localhost:6389/0"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    NVIDIA_API_KEY: str = "mock_key"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    GEMINI_API_KEY: str = "mock_key"
    
    CLERK_SECRET_KEY: str = "mock_clerk_secret"
    DEV_AUTH_BYPASS: bool = True
    
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
# Ensure DB directory exists if using SQLite fallback or ChromaDB
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
