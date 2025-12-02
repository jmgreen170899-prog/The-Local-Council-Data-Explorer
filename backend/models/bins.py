"""
Bins models module.

This module contains Pydantic models for bin collection data.
"""

from typing import List

from pydantic import BaseModel


class BinCollection(BaseModel):
    """Model representing a single bin collection."""

    type: str
    collection_date: str


class BinCollectionResponse(BaseModel):
    """Model representing a bin collection API response."""

    address: str
    council: str
    bins: List[BinCollection]
