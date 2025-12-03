"""
Bins models module.

This module contains Pydantic models for bin collection data.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class BinCollection(BaseModel):
    """Model representing a single bin collection."""

    type: str = Field(..., description="Type of bin (e.g., Refuse, Recycling, Garden)")
    collection_date: str = Field(
        ..., description="Next collection date in ISO format (YYYY-MM-DD)"
    )


class BinCollectionResponse(BaseModel):
    """Model representing a bin collection API response."""

    address: str = Field(..., description="Full address of the property")
    council: str = Field(..., description="Name of the local council")
    bins: List[BinCollection] = Field(
        default_factory=list, description="List of bin collection schedules"
    )


class BinCollectionRequest(BaseModel):
    """Model for bin collection request parameters."""

    postcode: Optional[str] = Field(
        default=None, description="UK postcode for the property"
    )
    house_number: Optional[str] = Field(
        default=None, description="House number or name"
    )
    uprn: Optional[str] = Field(
        default=None, description="Unique Property Reference Number"
    )


class ErrorResponse(BaseModel):
    """Model for error responses."""

    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
