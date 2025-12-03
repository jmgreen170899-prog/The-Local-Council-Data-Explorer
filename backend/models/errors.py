"""
Error models module.

This module contains Pydantic models for error responses used across the API.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Model for error responses."""

    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
