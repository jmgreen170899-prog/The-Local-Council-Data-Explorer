"""
Planning router module.

This module handles HTTP requests for planning application data.
"""

import logging
from typing import Annotated, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from config import Settings, get_settings
from models.errors import ErrorResponse
from models.planning import PlanningResponse
from services.planning_service import PlanningService, get_planning_service

logger = logging.getLogger(__name__)

router = APIRouter()


def get_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> PlanningService:
    """Dependency injection for PlanningService.

    Args:
        settings: Application settings from dependency injection.

    Returns:
        PlanningService instance.
    """
    return get_planning_service(settings)


@router.get(
    "/",
    response_model=PlanningResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "External Service Unavailable"},
    },
    summary="Get planning applications",
    description="Retrieve planning applications for a local planning authority. "
    "Optionally filter by date range.",
)
async def get_planning(
    service: Annotated[PlanningService, Depends(get_service)],
    lpa: Annotated[
        str,
        Query(
            description="Local Planning Authority name or identifier",
            example="City of York Council",
        ),
    ],
    date_from: Annotated[
        Optional[str],
        Query(
            description="Start date for filtering applications (YYYY-MM-DD)",
            example="2025-01-01",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ] = None,
    date_to: Annotated[
        Optional[str],
        Query(
            description="End date for filtering applications (YYYY-MM-DD)",
            example="2025-12-31",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ] = None,
) -> PlanningResponse:
    """Get planning applications for a local planning authority.

    Args:
        service: Injected PlanningService instance.
        lpa: Local Planning Authority name or identifier.
        date_from: Start date for filtering (YYYY-MM-DD).
        date_to: End date for filtering (YYYY-MM-DD).

    Returns:
        PlanningResponse with LPA name and list of planning applications.

    Raises:
        HTTPException: If the request is invalid or external service fails.
    """
    # Validate date range if both provided
    if date_from and date_to:
        if date_from > date_to:
            raise HTTPException(
                status_code=400,
                detail="date_from cannot be after date_to",
            )

    try:
        result = await service.get_planning_applications(
            lpa=lpa,
            date_from=date_from,
            date_to=date_to,
        )
        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except httpx.TimeoutException as e:
        logger.error(f"Timeout fetching planning applications: {e}")
        raise HTTPException(
            status_code=503,
            detail="External planning service timed out",
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching planning applications: {e}")
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="No planning data found for the provided LPA",
            )
        raise HTTPException(
            status_code=503,
            detail="External planning service returned an error",
        )
    except httpx.RequestError as e:
        logger.error(f"Request error fetching planning applications: {e}")
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to external planning service",
        )
    except Exception as e:
        logger.exception(f"Unexpected error fetching planning applications: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        )
