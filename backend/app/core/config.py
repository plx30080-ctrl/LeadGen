"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # App Info
    APP_NAME: str = "LeadGen"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://leadgen:leadgen_password@localhost:5432/leadgen_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Keys (to be set by user)
    OPENAI_API_KEY: Optional[str] = None
    INDEED_API_KEY: Optional[str] = None
    ZIPRECRUITER_API_KEY: Optional[str] = None
    LINKEDIN_API_KEY: Optional[str] = None
    ZOOMINFO_API_KEY: Optional[str] = None
    APOLLO_API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    # Feature Flags
    ENABLE_JOB_SCRAPING: bool = True
    ENABLE_LEAD_ENRICHMENT: bool = True
    ENABLE_AI_GENERATION: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Cache Settings
    CACHE_TTL_SECONDS: int = 3600
    DEDUPLICATION_TTL_DAYS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
