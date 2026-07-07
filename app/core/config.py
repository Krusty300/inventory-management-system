from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Inventory Management System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./inventory.db"
    
    # Optional: Add these if you want to use them later
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # This allows extra fields in the .env file without causing errors
        extra = "ignore"

settings = Settings()