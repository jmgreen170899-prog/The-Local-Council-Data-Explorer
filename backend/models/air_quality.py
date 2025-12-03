"""
Air quality models module.

This module contains Pydantic models for air quality data.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Pollutant(BaseModel):
    """Model representing a single pollutant measurement."""

    name: str = Field(..., description="Pollutant name (e.g., NO2, PM2.5, O3)")
    value: float = Field(..., description="Measured value of the pollutant")
    units: str = Field(..., description="Units of measurement (e.g., ug/m3)")
    band: Optional[str] = Field(
        default=None, description="Air quality band (Low, Moderate, High, Very High)"
    )
    index: Optional[int] = Field(
        default=None, description="DAQI index for this pollutant (1-10)"
    )


class AirQualityResponse(BaseModel):
    """Model representing an air quality API response."""

    area: str = Field(..., description="Geographic area name")
    max_daqi: int = Field(
        ...,
        ge=1,
        le=10,
        description="Maximum Daily Air Quality Index (1-10)",
    )
    summary: str = Field(
        ..., description="Summary of air quality (Low, Moderate, High, Very High)"
    )
    pollutants: List[Pollutant] = Field(
        default_factory=list, description="List of pollutant measurements"
    )
    forecast_date: Optional[str] = Field(
        default=None, description="Date of the forecast (YYYY-MM-DD)"
    )


class AirQualityRequest(BaseModel):
    """Model for air quality request parameters."""

    area: Optional[str] = Field(default=None, description="Geographic area to query")
