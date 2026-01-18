import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Attendance"
    PROJECT_VERSION: str = "1.0.0"
    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # Face Recognition Config
    SIMILARITY_THRESHOLD: float = 0.5  # Lower is stricter (0.6 is default usually)
    REQUIRED_CONSECUTIVE_FRAMES: int = 3
    
    # Database
    DATABASE_URL: str = "sqlite:///./attendance.db"

    class Config:
        env_file = ".env"

settings = Settings()
