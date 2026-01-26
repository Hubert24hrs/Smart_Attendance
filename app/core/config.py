from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Attendance Platform"
    PROJECT_VERSION: str = "4.0.0"
    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    
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
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@smartattendance.io"
    SMTP_TLS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Redis (for caching/sessions)
    REDIS_URL: Optional[str] = None
    
    @property
    def database_url_computed(self) -> str:
        if self.POSTGRES_HOST and self.POSTGRES_USER:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"
        return self.DATABASE_URL

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
