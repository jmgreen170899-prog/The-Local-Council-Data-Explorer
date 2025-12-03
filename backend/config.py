"""
Configuration module for the Local Council Data Explorer backend.

This module contains application-wide configuration settings such as:
- Database connection strings
- API keys
- Environment-specific settings
- External API base URLs and timeouts
- Mock mode configuration for offline/local development
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # -------------------------
    # Pydantic Settings Config
    # -------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",  # <- IMPORTANT: allows docker env vars (ENV, PORT, API_KEY)
    )

    # Basic app info
    APP_NAME: str = "Local Council Data Explorer"
    DEBUG: bool = Field(default=False)
    API_VERSION: str = "v1"

    # Environment variables for Docker / local dev
    env: str = "development"
    port: int = 8000
    api_key: str = "test"

    # Mock mode for offline/local development
    MOCK_MODE: bool = Field(default=True)

    # Database connection
    DATABASE_URL: Optional[str] = None

    # External API keys
    BINS_API_KEY: Optional[str] = None
    PLANNING_API_KEY: Optional[str] = None
    AIR_QUALITY_API_KEY: Optional[str] = None

    # Base URLs for external APIs
    BINS_API_BASE_URL: str = "https://waste-api.york.gov.uk/api/Collections"
    PLANNING_API_BASE_URL: str = "https://www.planning.data.gov.uk"
    AIR_QUALITY_API_BASE_URL: str = "https://api.erg.ic.ac.uk/AirQuality"

    # Cache TTLs (seconds)
    CACHE_TTL_BINS: int = 3600
    CACHE_TTL_PLANNING: int = 1800
    CACHE_TTL_AIR_QUALITY: int = 600

    # HTTP timeouts
    HTTP_TIMEOUT: float = 30.0
    HTTP_CONNECT_TIMEOUT: float = 10.0

    # Retry settings
    HTTP_MAX_RETRIES: int = 3


def get_settings() -> Settings:
    """Return an instance of application settings."""
    return Settings()


settings = get_settings()
