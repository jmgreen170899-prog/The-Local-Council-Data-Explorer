"""
Planning models module.

This module contains Pydantic models for planning application data.
"""

from typing import List

from pydantic import BaseModel


class PlanningApplication(BaseModel):
    """Model representing a single planning application."""

    reference: str
    address: str
    proposal: str
    status: str
    received_date: str


class PlanningResponse(BaseModel):
    """Model representing a planning applications API response."""

    lpa: str
    applications: List[PlanningApplication]
