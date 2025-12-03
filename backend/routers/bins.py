"""
Bins router module.

This module handles HTTP requests for bin collection data.
"""

import logging
from typing import Annotated, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from config import Settings, get_settings
from models.bins import BinCollectionResponse
from models.errors import ErrorResponse
from services.bins_service import BinsService, get_bins_service

logger = logging.getLogger(__name__)

router = APIRouter()


def get_service(settings: Annotated[Settings, Depends(get_settings)]) -> BinsService:
    """Dependency injection for BinsService.

    Args:
        settings: Application settings from dependency injection.

    Returns:
        BinsService instance.
    """
    return get_bins_service(settings)


@router.get(
    "/",
    response_model=BinCollectionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "External Service Unavailable"},
    },
    summary="Get bin collection schedule",
    description="Retrieve bin collection schedule for a property. "
    "Provide either postcode + house_number, or UPRN.",
)
async def get_bins(
    service: Annotated[BinsService, Depends(get_service)],
    postcode: Annotated[
        Optional[str],
        Query(
            description="UK postcode for the property",
            examples=["YO1 1AA"],
        ),
    ] = None,
    house_number: Annotated[
        Optional[str],
        Query(
            description="House number or name",
            examples=["10"],
        ),
    ] = None,
    uprn: Annotated[
        Optional[str],
        Query(
            description="Unique Property Reference Number",
            examples=["100070123456"],
        ),
    ] = None,
) -> BinCollectionResponse:
    """Get bin collection schedule for a property.

    Args:
        service: Injected BinsService instance.
        postcode: UK postcode for the property.
        house_number: House number or name.
        uprn: Unique Property Reference Number.

    Returns:
        BinCollectionResponse with address, council, and bin collection details.

    Raises:
        HTTPException: If the request is invalid or external service fails.
    """
    # Validate input - need either UPRN or postcode
    if not uprn and not postcode:
        raise HTTPException(
            status_code=400,
            detail="Either 'postcode' or 'uprn' must be provided",
        )

    try:
        result = await service.get_bin_collections(
            postcode=postcode,
            house_number=house_number,
            uprn=uprn,
        )
        return result

    except httpx.TimeoutException as e:
        logger.error(f"Timeout fetching bin collections: {e}")
        raise HTTPException(
            status_code=503,
            detail="External bin collection service timed out",
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching bin collections: {e}")
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="No bin collection data found for the provided address",
            )
        raise HTTPException(
            status_code=503,
            detail="External bin collection service returned an error",
        )
    except httpx.RequestError as e:
        logger.error(f"Request error fetching bin collections: {e}")
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to external bin collection service",
        )
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error fetching bin collections: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        )
