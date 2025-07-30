from functools import lru_cache
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"  # Allow extra fields to prevent validation errors
    )

    # Database Configuration - PostgreSQL ONLY
    # IMPORTANT: SQLite has been removed due to concurrency and performance issues
    # This application now requires PostgreSQL for proper operation
    DATABASE_URL: Optional[str] = None
    
    # PostgreSQL specific settings
    POSTGRES_USER: str = "notesgen"
    POSTGRES_PASSWORD: str = "notesgen_password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "notesgen_db"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Build database connection string.
        Temporarily using SQLite for development until PostgreSQL is properly configured.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # Temporary fallback to SQLite for development
        return "sqlite:///./notesgen.db"

    # AWS - Read from environment variables ONLY (no hardcoded fallbacks for security)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_DEFAULT_REGION: str = "us-east-1"
    AWS_BUCKET_NAME: str = "notesgen-files-prod"

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50000000  # 50MB

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load AWS credentials from environment variables
        self.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        # Validate that AWS credentials are provided
        if not self.AWS_ACCESS_KEY_ID:
            print("⚠️  WARNING: AWS_ACCESS_KEY_ID not found in environment variables")
        if not self.AWS_SECRET_ACCESS_KEY:
            print("⚠️  WARNING: AWS_SECRET_ACCESS_KEY not found in environment variables")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
