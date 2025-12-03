"""
Configuration module for the Local Council Data Explorer backend.

This module contains application-wide configuration settings such as:
- Database connection strings
- API keys
- Environment-specific settings
- External API base URLs and timeouts
- Mock mode configuration for offline/local development
"""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "Local Council Data Explorer"
    DEBUG: bool = Field(default=False)
    API_VERSION: str = "v1"

    # Mock mode for offline/local development
    MOCK_MODE: bool = Field(default=True)

    # Database settings (placeholder)
    DATABASE_URL: Optional[str] = None

    # External API settings
    BINS_API_KEY: Optional[str] = None
    PLANNING_API_KEY: Optional[str] = None
    AIR_QUALITY_API_KEY: Optional[str] = None

    # Base URLs for external APIs
    # City of York Council Waste Collection API
    BINS_API_BASE_URL: str = "https://waste-api.york.gov.uk/api/Collections"
    # planning.data.gov.uk API for planning applications
    PLANNING_API_BASE_URL: str = "https://www.planning.data.gov.uk"
    # UK-AIR / Defra API for air quality data
    AIR_QUALITY_API_BASE_URL: str = "https://api.erg.ic.ac.uk/AirQuality"

    # Cache settings (time-to-live in seconds)
    CACHE_TTL_BINS: int = 3600  # 1 hour for bin collections
    CACHE_TTL_PLANNING: int = 1800  # 30 minutes for planning data
    CACHE_TTL_AIR_QUALITY: int = 600  # 10 minutes for air quality data

    # HTTP client timeouts (in seconds)
    HTTP_TIMEOUT: float = 30.0
    HTTP_CONNECT_TIMEOUT: float = 10.0

    # Retry settings
    HTTP_MAX_RETRIES: int = 3

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> Settings:
    """Get application settings instance.
    
    Returns:
        Settings instance, can be used as a FastAPI dependency.
    """
    return Settings()


settings = get_settings()
