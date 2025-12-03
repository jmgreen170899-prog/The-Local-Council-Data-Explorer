"""
Air quality router module.

This module handles HTTP requests for air quality data.
"""

import logging
from typing import Annotated, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from config import Settings, get_settings
from models.air_quality import AirQualityResponse
from models.errors import ErrorResponse
from services.air_service import AirQualityService, get_air_quality_service

logger = logging.getLogger(__name__)

router = APIRouter()


def get_service(
    settings: Annotated[Settings, Depends(get_settings)]
) -> AirQualityService:
    """Dependency injection for AirQualityService.
    
    Args:
        settings: Application settings from dependency injection.
        
    Returns:
        AirQualityService instance.
    """
    return get_air_quality_service(settings)


@router.get(
    "/",
    response_model=AirQualityResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "External Service Unavailable"},
    },
    summary="Get air quality data",
    description="Retrieve current air quality data and DAQI index for an area. "
    "If no area is specified, returns data for the default region.",
)
async def get_air_quality(
    service: Annotated[AirQualityService, Depends(get_service)],
    area: Annotated[
        Optional[str],
        Query(
            description="Geographic area or region to query",
            example="Greater London",
        ),
    ] = None,
) -> AirQualityResponse:
    """Get air quality data for an area.
    
    Args:
        service: Injected AirQualityService instance.
        area: Geographic area or region name. Defaults to "Yorkshire & Humber".
        
    Returns:
        AirQualityResponse with DAQI index, summary, and pollutant breakdown.
        
    Raises:
        HTTPException: If the external service fails.
    """
    try:
        result = await service.get_air_quality(area=area)
        return result

    except httpx.TimeoutException as e:
        logger.error(f"Timeout fetching air quality data: {e}")
        raise HTTPException(
            status_code=503,
            detail="External air quality service timed out",
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching air quality data: {e}")
        raise HTTPException(
            status_code=503,
            detail="External air quality service returned an error",
        )
    except httpx.RequestError as e:
        logger.error(f"Request error fetching air quality data: {e}")
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to external air quality service",
        )
    except Exception as e:
        logger.exception(f"Unexpected error fetching air quality data: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        )
