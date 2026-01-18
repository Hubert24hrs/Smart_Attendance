import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Attendance"
    PROJECT_VERSION: str = "3.0.0"
    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # Face Recognition Config
    SIMILARITY_THRESHOLD: float = 0.5
    REQUIRED_CONSECUTIVE_FRAMES: int = 3
    
    # Database
    DATABASE_URL: str = "sqlite:///./attendance.db"
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    
    # Email/SMTP Configuration
    SMTP_HOST: Optional[str] = None  # e.g., smtp.gmail.com
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "attendance@school.edu"
    SMTP_TLS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @property
    def database_url_computed(self) -> str:
        if self.POSTGRES_HOST and self.POSTGRES_USER:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"
        return self.DATABASE_URL

    class Config:
        env_file = ".env"

settings = Settings()
