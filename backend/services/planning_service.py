"""
Planning service module.

This module contains business logic for planning application data retrieval and processing.
Implements async HTTP calls using httpx and provides mock data for offline development.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from config import Settings, get_settings
from models.planning import PlanningApplication, PlanningResponse

logger = logging.getLogger(__name__)


# Mock data for offline/local development
MOCK_PLANNING_DATA: Dict[str, List[PlanningApplication]] = {
    "City of York Council": [
        PlanningApplication(
            reference="23/12345/FUL",
            address="12 Example Road, York, YO1 1AB",
            proposal="Erection of single storey rear extension",
            status="Pending Consideration",
            received_date="2025-11-10",
            application_type="Full Application",
        ),
        PlanningApplication(
            reference="23/12346/HOU",
            address="45 Sample Street, York, YO2 2CD",
            proposal="Loft conversion with rear dormer window",
            status="Approved",
            received_date="2025-10-15",
            decision_date="2025-11-20",
            decision="Approved",
            application_type="Householder",
        ),
        PlanningApplication(
            reference="23/12347/OUT",
            address="Land North of Main Road, York",
            proposal="Outline application for residential development (10 dwellings)",
            status="Under Review",
            received_date="2025-09-01",
            application_type="Outline Application",
        ),
    ],
    "Westminster City Council": [
        PlanningApplication(
            reference="23/07890/FULL",
            address="100 Victoria Street, London, SW1E 5JL",
            proposal="Change of use from office to residential",
            status="Pending",
            received_date="2025-11-05",
            application_type="Full Application",
        ),
    ],
    "Manchester City Council": [
        PlanningApplication(
            reference="135678/FO/2025",
            address="Piccadilly Plaza, Manchester, M1 4AH",
            proposal="Internal alterations to ground floor retail unit",
            status="Decided",
            received_date="2025-10-01",
            decision_date="2025-11-15",
            decision="Granted",
            application_type="Full Application",
        ),
    ],
}


class PlanningService:
    """Service for retrieving planning application data."""

    def __init__(self, settings: Settings):
        """Initialize the planning service.
        
        Args:
            settings: Application settings instance.
        """
        self.settings = settings
        self.base_url = settings.PLANNING_API_BASE_URL
        self.timeout = httpx.Timeout(
            timeout=settings.HTTP_TIMEOUT,
            connect=settings.HTTP_CONNECT_TIMEOUT,
        )

    async def get_planning_applications(
        self,
        lpa: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> PlanningResponse:
        """Retrieve planning applications for a given local planning authority.

        Args:
            lpa: Local Planning Authority identifier.
            date_from: Start date for filtering applications (YYYY-MM-DD).
            date_to: End date for filtering applications (YYYY-MM-DD).

        Returns:
            PlanningResponse containing LPA and planning application details.

        Raises:
            httpx.HTTPError: If the external API call fails.
            ValueError: If lpa is not provided.
        """
        if not lpa:
            raise ValueError("Local Planning Authority (lpa) is required")

        if self.settings.MOCK_MODE:
            return self._get_mock_data(lpa, date_from, date_to)

        return await self._fetch_from_api(lpa, date_from, date_to)

    def _get_mock_data(
        self,
        lpa: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> PlanningResponse:
        """Get mock planning application data for development.

        Args:
            lpa: Local Planning Authority identifier.
            date_from: Start date for filtering.
            date_to: End date for filtering.

        Returns:
            Mock PlanningResponse data.
        """
        logger.info("Using mock data for planning applications")

        # Find matching LPA in mock data
        applications: List[PlanningApplication] = []
        matched_lpa = lpa

        for lpa_name, apps in MOCK_PLANNING_DATA.items():
            if lpa.lower() in lpa_name.lower() or lpa_name.lower() in lpa.lower():
                applications = apps.copy()
                matched_lpa = lpa_name
                break

        # If no match found, return first available mock data
        if not applications:
            first_lpa = next(iter(MOCK_PLANNING_DATA))
            applications = MOCK_PLANNING_DATA[first_lpa].copy()
            matched_lpa = first_lpa

        # Apply date filters if provided
        if date_from or date_to:
            applications = self._filter_by_date(applications, date_from, date_to)

        return PlanningResponse(
            lpa=matched_lpa,
            applications=applications,
            total_count=len(applications),
        )

    def _filter_by_date(
        self,
        applications: List[PlanningApplication],
        date_from: Optional[str],
        date_to: Optional[str],
    ) -> List[PlanningApplication]:
        """Filter applications by date range.

        Args:
            applications: List of applications to filter.
            date_from: Start date (YYYY-MM-DD).
            date_to: End date (YYYY-MM-DD).

        Returns:
            Filtered list of applications.
        """
        filtered = []
        for app in applications:
            try:
                app_date = datetime.strptime(app.received_date, "%Y-%m-%d")

                if date_from:
                    from_date = datetime.strptime(date_from, "%Y-%m-%d")
                    if app_date < from_date:
                        continue

                if date_to:
                    to_date = datetime.strptime(date_to, "%Y-%m-%d")
                    if app_date > to_date:
                        continue

                filtered.append(app)
            except ValueError:
                # If date parsing fails, include the application
                filtered.append(app)

        return filtered

    async def _fetch_from_api(
        self,
        lpa: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> PlanningResponse:
        """Fetch planning application data from external API.

        Args:
            lpa: Local Planning Authority identifier.
            date_from: Start date for filtering.
            date_to: End date for filtering.

        Returns:
            PlanningResponse from external API.

        Raises:
            httpx.HTTPError: If the API call fails.
        """
        params: Dict[str, Any] = {"lpa": lpa}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to

        headers = {}
        if self.settings.PLANNING_API_KEY:
            headers["Authorization"] = f"Bearer {self.settings.PLANNING_API_KEY}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/applications",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_api_response(data, lpa)

    def _parse_api_response(
        self, data: Dict[str, Any], lpa: str
    ) -> PlanningResponse:
        """Parse raw API response into PlanningResponse model.

        Args:
            data: Raw response data from external API.
            lpa: Local Planning Authority name.

        Returns:
            Normalized PlanningResponse.
        """
        applications: List[PlanningApplication] = []
        raw_apps = data.get("applications", data.get("results", []))

        for app in raw_apps:
            applications.append(
                PlanningApplication(
                    reference=app.get("reference", app.get("app_ref", "")),
                    address=app.get("address", app.get("site_address", "")),
                    proposal=app.get("proposal", app.get("description", "")),
                    status=app.get("status", app.get("decision_status", "Unknown")),
                    received_date=app.get(
                        "received_date", app.get("date_received", "")
                    ),
                    decision_date=app.get("decision_date"),
                    decision=app.get("decision"),
                    applicant_name=app.get("applicant_name", app.get("applicant")),
                    application_type=app.get(
                        "application_type", app.get("app_type")
                    ),
                )
            )

        return PlanningResponse(
            lpa=data.get("lpa", lpa),
            applications=applications,
            total_count=data.get("total_count", len(applications)),
        )


def get_planning_service(settings: Settings = None) -> PlanningService:
    """Factory function to create PlanningService instance.
    
    Args:
        settings: Optional settings instance. If not provided, uses default settings.
    
    Returns:
        PlanningService instance.
    """
    if settings is None:
        settings = get_settings()
    return PlanningService(settings)
