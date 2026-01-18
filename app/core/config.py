import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Attendance"
    PROJECT_VERSION: str = "2.0.0"
    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # Face Recognition Config
    SIMILARITY_THRESHOLD: float = 0.5  # Lower is stricter
    REQUIRED_CONSECUTIVE_FRAMES: int = 3  # N-frame rule
    
    # Database - Supports SQLite (default) or PostgreSQL
    # For PostgreSQL: postgresql://user:password@host:5432/dbname
    DATABASE_URL: str = "sqlite:///./attendance.db"
    
    # Optional: PostgreSQL specific settings (used in Docker)
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    
    @property
    def database_url_computed(self) -> str:
        """Returns PostgreSQL URL if configured, else SQLite"""
        if self.POSTGRES_HOST and self.POSTGRES_USER:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"
        return self.DATABASE_URL

    class Config:
        env_file = ".env"

settings = Settings()
