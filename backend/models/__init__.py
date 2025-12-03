"""
Models package for the Local Council Data Explorer backend.

This package contains Pydantic models for data validation and serialization.
"""

from models.air_quality import AirQualityRequest, AirQualityResponse, Pollutant
from models.bins import (
    BinCollection,
    BinCollectionRequest,
    BinCollectionResponse,
)
from models.errors import ErrorResponse
from models.planning import PlanningApplication, PlanningRequest, PlanningResponse

__all__ = [
    # Bins models
    "BinCollection",
    "BinCollectionRequest",
    "BinCollectionResponse",
    # Planning models
    "PlanningApplication",
    "PlanningRequest",
    "PlanningResponse",
    # Air quality models
    "AirQualityRequest",
    "AirQualityResponse",
    "Pollutant",
    # Error models
    "ErrorResponse",
]
