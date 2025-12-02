"""
Air quality models module.

This module contains Pydantic models for air quality data.
"""

from typing import List, Optional

from pydantic import BaseModel


class Pollutant(BaseModel):
    """Model representing a single pollutant measurement."""

    name: str
    value: float
    units: str


class AirQualityResponse(BaseModel):
    """Model representing an air quality API response."""

    area: str
    max_daqi: int
    summary: str
    pollutants: List[Pollutant]
