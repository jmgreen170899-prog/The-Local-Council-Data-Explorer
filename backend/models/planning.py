"""
Planning models module.

This module contains Pydantic models for planning application data.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class PlanningApplication(BaseModel):
    """Model representing a single planning application."""

    reference: str = Field(..., description="Planning application reference number")
    address: str = Field(..., description="Site address for the application")
    proposal: str = Field(..., description="Description of the proposed development")
    status: str = Field(..., description="Current status of the application")
    received_date: str = Field(
        ..., description="Date application was received (YYYY-MM-DD)"
    )
    decision_date: Optional[str] = Field(
        default=None, description="Date of decision if available"
    )
    decision: Optional[str] = Field(
        default=None, description="Decision outcome if available"
    )
    applicant_name: Optional[str] = Field(
        default=None, description="Name of the applicant"
    )
    application_type: Optional[str] = Field(
        default=None, description="Type of planning application"
    )


class PlanningResponse(BaseModel):
    """Model representing a planning applications API response."""

    lpa: str = Field(..., description="Local Planning Authority name")
    applications: List[PlanningApplication] = Field(
        default_factory=list, description="List of planning applications"
    )
    total_count: int = Field(
        default=0, description="Total number of applications matching criteria"
    )


class PlanningRequest(BaseModel):
    """Model for planning applications request parameters."""

    lpa: str = Field(..., description="Local Planning Authority identifier")
    date_from: Optional[str] = Field(
        default=None, description="Start date for filtering (YYYY-MM-DD)"
    )
    date_to: Optional[str] = Field(
        default=None, description="End date for filtering (YYYY-MM-DD)"
    )
