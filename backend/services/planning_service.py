"""
Planning service module.

This module contains business logic for planning application data retrieval and processing.

Implements async HTTP calls using httpx to the planning.data.gov.uk API.
The API endpoint is: https://www.planning.data.gov.uk/entity.json

Data Flow:
1. Request comes in with LPA (Local Planning Authority) and optional date filters
2. Check cache for existing data
3. If not cached, fetch from planning.data.gov.uk API
4. Transform raw JSON response into internal PlanningResponse model
5. Cache the result for future requests
6. Return normalized response

Transformation Details:
- The planning.data.gov.uk API returns entity data with fields like:
  - "entities": array of planning entities
  - Each entity has: "entity", "reference", "name", "point", "entry-date", etc.
- We transform this into our internal model which has:
  - lpa: Local Planning Authority name
  - applications: List of PlanningApplication with reference, address, proposal, etc.
  - total_count: Total number of applications

Fallback Behavior:
- If API returns empty/null fields, we provide sensible defaults
- If API is unavailable, cached data is returned if available
- If no data available, returns empty applications list
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from config import Settings, get_settings
from models.planning import PlanningApplication, PlanningResponse
from services.cache import get_planning_cache, InMemoryCache

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

# Mapping of planning.data.gov.uk status values to user-friendly status
STATUS_MAPPING: Dict[str, str] = {
    "pending": "Pending Consideration",
    "approved": "Approved",
    "refused": "Refused",
    "withdrawn": "Withdrawn",
    "decided": "Decided",
    "registered": "Registered",
    "awaiting-decision": "Awaiting Decision",
    "in-progress": "In Progress",
}


class PlanningService:
    """Service for retrieving planning application data from planning.data.gov.uk.

    This service wraps the planning.data.gov.uk API and transforms the response
    into our internal data model.

    Attributes:
        settings: Application settings instance.
        base_url: Base URL for the planning.data.gov.uk API.
        timeout: HTTP timeout configuration.
        cache: In-memory cache for planning data.
    """

    def __init__(self, settings: Settings, cache: Optional[InMemoryCache] = None):
        """Initialize the planning service.

        Args:
            settings: Application settings instance.
            cache: Optional cache instance. If not provided, uses global cache.
        """
        self.settings = settings
        self.base_url = settings.PLANNING_API_BASE_URL
        self.timeout = httpx.Timeout(
            timeout=settings.HTTP_TIMEOUT,
            connect=settings.HTTP_CONNECT_TIMEOUT,
        )
        self.cache = cache or get_planning_cache()

    async def get_planning_applications(
        self,
        lpa: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> PlanningResponse:
        """Retrieve planning applications for a given local planning authority.

        This method first checks the cache for existing data. If not found,
        it fetches from the planning.data.gov.uk API and caches the result.

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

        # Generate cache key based on input parameters
        cache_key = self.cache.generate_key(
            "planning", lpa=lpa, date_from=date_from, date_to=date_to
        )

        # Check cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"Returning cached planning data for key: {cache_key}")
            return cached

        if self.settings.MOCK_MODE:
            result = self._get_mock_data(lpa, date_from, date_to)
        else:
            result = await self._fetch_from_api(lpa, date_from, date_to)

        # Cache the result
        self.cache.set(cache_key, result, ttl=self.settings.CACHE_TTL_PLANNING)
        return result

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
        """Fetch planning application data from planning.data.gov.uk API.

        The API endpoint format is:
        GET https://www.planning.data.gov.uk/entity.json

        Query parameters:
        - dataset: planning-application
        - organisation_entity: LPA entity ID (or use search)
        - entry_date_year/month/day: Filter by entry date

        Args:
            lpa: Local Planning Authority identifier.
            date_from: Start date for filtering.
            date_to: End date for filtering.

        Returns:
            PlanningResponse from external API.

        Raises:
            httpx.HTTPError: If the API call fails.
        """
        # Build query parameters for planning.data.gov.uk API
        params: Dict[str, Any] = {
            "dataset": "planning-application",
            "limit": 100,  # Limit results
        }

        # Add date filters if provided
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                params["entry_date_year"] = from_date.year
                params["entry_date_month"] = from_date.month
                params["entry_date_day"] = from_date.day
                params["entry_date_match"] = "after"
            except ValueError:
                logger.warning(f"Invalid date_from format: {date_from}")

        url = f"{self.base_url}/entity.json"

        logger.info(f"Fetching planning data from: {url} with params: {params}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            return self._transform_planning_api_response(data, lpa, date_from, date_to)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from planning.data.gov.uk: {e}")
            # Return empty response on error
            return self._create_fallback_response(lpa)
        except httpx.RequestError as e:
            logger.error(f"Request error connecting to planning.data.gov.uk: {e}")
            raise

    def _transform_planning_api_response(
        self,
        data: Any,
        lpa: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> PlanningResponse:
        """Transform planning.data.gov.uk API response into internal model.

        The planning.data.gov.uk API returns data in the following structure:
        {
            "entities": [
                {
                    "entity": 12345,
                    "reference": "23/12345/FUL",
                    "name": "Planning Application at 12 Example Road",
                    "entry-date": "2025-11-10",
                    "start-date": "2025-11-10",
                    "point": "POINT(-1.080 53.958)",
                    "organisation-entity": "329",
                    ...
                },
                ...
            ],
            "count": 100
        }

        Args:
            data: Raw JSON response from planning.data.gov.uk API.
            lpa: Local Planning Authority name for the response.
            date_from: Start date for filtering.
            date_to: End date for filtering.

        Returns:
            Normalized PlanningResponse.
        """
        applications: List[PlanningApplication] = []

        # Handle different response formats
        if isinstance(data, dict):
            # Extract entities array
            entities = data.get("entities", [])

            for entity in entities:
                app = self._parse_entity(entity)
                if app:
                    applications.append(app)

        elif isinstance(data, list):
            # If response is directly a list of entities
            for entity in data:
                app = self._parse_entity(entity)
                if app:
                    applications.append(app)

        # Apply date filters to the transformed data
        if date_from or date_to:
            applications = self._filter_by_date(applications, date_from, date_to)

        # Sort by received date, most recent first
        applications = self._sort_applications_by_date(applications)

        return PlanningResponse(
            lpa=lpa,
            applications=applications,
            total_count=len(applications),
        )

    def _parse_entity(self, entity: Dict[str, Any]) -> Optional[PlanningApplication]:
        """Parse a single entity from planning.data.gov.uk into PlanningApplication.

        Handles the entity format from the API and extracts relevant fields.

        Args:
            entity: Single entity object from API response.

        Returns:
            PlanningApplication if parsing succeeds, None otherwise.
        """
        # Skip if entity is empty or not a dict
        if not entity or not isinstance(entity, dict):
            return None

        # Extract reference - required field
        reference = (
            entity.get("reference")
            or entity.get("planning-application-reference")
            or entity.get("name", "")
        )

        if not reference:
            return None

        # Extract address from name or geometry
        address = self._extract_address(entity)

        # Extract proposal/description
        proposal = (
            entity.get("description")
            or entity.get("name")
            or entity.get("notes")
            or "Planning application"
        )

        # Extract and normalize status
        raw_status = entity.get("planning-decision", "")
        status = self._normalize_status(raw_status)

        # Extract dates
        received_date = self._normalize_date(
            entity.get("entry-date")
            or entity.get("start-date")
            or entity.get("received-date")
            or ""
        )

        decision_date = self._normalize_date(
            entity.get("decision-date") or entity.get("end-date") or ""
        )

        # Extract decision outcome
        decision = entity.get("planning-decision") or None

        # Extract applicant if available
        applicant_name = entity.get("applicant-name") or None

        # Extract application type
        application_type = (
            entity.get("planning-application-type")
            or entity.get("development-type")
            or None
        )

        return PlanningApplication(
            reference=reference,
            address=address,
            proposal=proposal,
            status=status,
            received_date=received_date,
            decision_date=decision_date if decision_date else None,
            decision=decision,
            applicant_name=applicant_name,
            application_type=application_type,
        )

    def _extract_address(self, entity: Dict[str, Any]) -> str:
        """Extract address from entity data.

        Tries multiple field names and falls back to coordinates if needed.

        Args:
            entity: Entity object from API.

        Returns:
            Address string.
        """
        # Try direct address fields
        address = (
            entity.get("address")
            or entity.get("site-address")
            or entity.get("address-text")
        )

        if address:
            return str(address)

        # Try to construct from name
        name = entity.get("name", "")
        if name and "at" in name.lower():
            # Extract address part after "at"
            parts = name.lower().split(" at ", 1)
            if len(parts) > 1:
                return parts[1].title()

        # Fall back to name or reference
        return name or entity.get("reference", "Unknown Address")

    def _normalize_status(self, status: str) -> str:
        """Normalize status to user-friendly value.

        Args:
            status: Raw status from API.

        Returns:
            Normalized status string.
        """
        if not status:
            return "Pending"

        lower_status = status.lower().strip()

        if lower_status in STATUS_MAPPING:
            return STATUS_MAPPING[lower_status]

        # Return title case of original
        return status.title()

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to ISO format (YYYY-MM-DD).

        Args:
            date_str: Raw date string from API.

        Returns:
            Date in YYYY-MM-DD format, or empty string if parsing fails.
        """
        if not date_str:
            return ""

        date_str = str(date_str).strip()

        # Try different date formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%d/%m/%Y",
            "%d-%m-%Y",
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_str}")
        return date_str

    def _sort_applications_by_date(
        self, applications: List[PlanningApplication]
    ) -> List[PlanningApplication]:
        """Sort applications by received date, most recent first.

        Args:
            applications: List of PlanningApplication objects.

        Returns:
            Sorted list of applications.
        """

        def parse_date(app: PlanningApplication) -> datetime:
            try:
                return datetime.strptime(app.received_date, "%Y-%m-%d")
            except ValueError:
                return datetime.min

        return sorted(applications, key=parse_date, reverse=True)

    def _create_fallback_response(self, lpa: str) -> PlanningResponse:
        """Create a fallback response when API data is unavailable.

        Args:
            lpa: Local Planning Authority name.

        Returns:
            PlanningResponse with empty applications list.
        """
        return PlanningResponse(
            lpa=lpa,
            applications=[],
            total_count=0,
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
