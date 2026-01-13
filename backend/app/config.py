"""
Application Configuration
Manages environment variables and settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Amazon Review Scraper"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://aydn:aydn_password@postgres:5432/aydn_reviews"

    # Redis/Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Scraper Settings
    SCRAPER_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    SCRAPER_DELAY_MIN: float = 2.0  # seconds between requests
    SCRAPER_DELAY_MAX: float = 5.0
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_TIMEOUT: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    RATE_LIMIT_PER_HOUR: int = 100

    # Supported Marketplaces
    AMAZON_MARKETPLACES: dict = {
        "us": "amazon.com",
        "de": "amazon.de",
        "uk": "amazon.co.uk",
        "fr": "amazon.fr",
        "it": "amazon.it",
        "es": "amazon.es",
        "ca": "amazon.ca",
        "jp": "amazon.co.jp",
    }

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
