"""
Configuration module for the Local Council Data Explorer backend.

This module contains application-wide configuration settings such as:
- Database connection strings
- API keys
- Environment-specific settings
"""

from typing import Optional


class Settings:
    """Application settings."""

    APP_NAME: str = "Local Council Data Explorer"
    DEBUG: bool = False
    API_VERSION: str = "v1"

    # Database settings (placeholder)
    DATABASE_URL: Optional[str] = None

    # External API settings (placeholder)
    BINS_API_KEY: Optional[str] = None
    PLANNING_API_KEY: Optional[str] = None
    AIR_QUALITY_API_KEY: Optional[str] = None


settings = Settings()
