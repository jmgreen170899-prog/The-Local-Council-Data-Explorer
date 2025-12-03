"""
Air quality service module.

This module contains business logic for air quality data retrieval and processing.
Implements async HTTP calls using httpx and provides mock data for offline development.
Uses the UK Air Quality Index (DAQI) scale from 1-10.
"""

import logging
from datetime import date
from typing import Any, Dict, List, Optional

import httpx

from config import Settings, get_settings
from models.air_quality import AirQualityResponse, Pollutant

logger = logging.getLogger(__name__)


# DAQI band definitions
DAQI_BANDS = {
    (1, 3): "Low",
    (4, 6): "Moderate",
    (7, 9): "High",
    (10, 10): "Very High",
}


def get_daqi_summary(index: int) -> str:
    """Get DAQI summary text for a given index value.
    
    Args:
        index: DAQI index value (1-10).
        
    Returns:
        Summary text (Low, Moderate, High, or Very High).
    """
    for (low, high), summary in DAQI_BANDS.items():
        if low <= index <= high:
            return summary
    return "Unknown"


# Mock data for offline/local development
MOCK_AIR_QUALITY_DATA: Dict[str, AirQualityResponse] = {
    "Yorkshire & Humber": AirQualityResponse(
        area="Yorkshire & Humber",
        max_daqi=2,
        summary="Low",
        pollutants=[
            Pollutant(name="NO2", value=18.5, units="µg/m³", band="Low", index=1),
            Pollutant(name="PM2.5", value=6.2, units="µg/m³", band="Low", index=1),
            Pollutant(name="PM10", value=12.4, units="µg/m³", band="Low", index=1),
            Pollutant(name="O3", value=45.0, units="µg/m³", band="Low", index=2),
        ],
        forecast_date=date.today().isoformat(),
    ),
    "Greater London": AirQualityResponse(
        area="Greater London",
        max_daqi=4,
        summary="Moderate",
        pollutants=[
            Pollutant(name="NO2", value=42.0, units="µg/m³", band="Moderate", index=3),
            Pollutant(name="PM2.5", value=18.5, units="µg/m³", band="Moderate", index=4),
            Pollutant(name="PM10", value=28.3, units="µg/m³", band="Low", index=2),
            Pollutant(name="O3", value=52.0, units="µg/m³", band="Low", index=2),
            Pollutant(name="SO2", value=8.0, units="µg/m³", band="Low", index=1),
        ],
        forecast_date=date.today().isoformat(),
    ),
    "Greater Manchester": AirQualityResponse(
        area="Greater Manchester",
        max_daqi=3,
        summary="Low",
        pollutants=[
            Pollutant(name="NO2", value=28.0, units="µg/m³", band="Low", index=2),
            Pollutant(name="PM2.5", value=10.5, units="µg/m³", band="Low", index=2),
            Pollutant(name="PM10", value=18.0, units="µg/m³", band="Low", index=2),
            Pollutant(name="O3", value=58.0, units="µg/m³", band="Low", index=3),
        ],
        forecast_date=date.today().isoformat(),
    ),
    "West Midlands": AirQualityResponse(
        area="West Midlands",
        max_daqi=3,
        summary="Low",
        pollutants=[
            Pollutant(name="NO2", value=25.0, units="µg/m³", band="Low", index=2),
            Pollutant(name="PM2.5", value=9.0, units="µg/m³", band="Low", index=2),
            Pollutant(name="PM10", value=15.0, units="µg/m³", band="Low", index=1),
            Pollutant(name="O3", value=60.0, units="µg/m³", band="Low", index=3),
        ],
        forecast_date=date.today().isoformat(),
    ),
}


class AirQualityService:
    """Service for retrieving air quality data."""

    def __init__(self, settings: Settings):
        """Initialize the air quality service.
        
        Args:
            settings: Application settings instance.
        """
        self.settings = settings
        self.base_url = settings.AIR_QUALITY_API_BASE_URL
        self.timeout = httpx.Timeout(
            timeout=settings.HTTP_TIMEOUT,
            connect=settings.HTTP_CONNECT_TIMEOUT,
        )

    async def get_air_quality(
        self,
        area: Optional[str] = None,
    ) -> AirQualityResponse:
        """Retrieve air quality data for a given area.

        Args:
            area: The geographic area to get air quality data for.
                  If not provided, defaults to "Yorkshire & Humber".

        Returns:
            AirQualityResponse containing DAQI index, summary, and pollutant breakdown.

        Raises:
            httpx.HTTPError: If the external API call fails.
        """
        if self.settings.MOCK_MODE:
            return self._get_mock_data(area)

        return await self._fetch_from_api(area)

    def _get_mock_data(self, area: Optional[str] = None) -> AirQualityResponse:
        """Get mock air quality data for development.

        Args:
            area: The geographic area to query.

        Returns:
            Mock AirQualityResponse data.
        """
        logger.info("Using mock data for air quality")

        # Default area if not provided
        if not area:
            return MOCK_AIR_QUALITY_DATA["Yorkshire & Humber"]

        # Try to find matching area in mock data
        area_lower = area.lower()
        for mock_area, response in MOCK_AIR_QUALITY_DATA.items():
            if area_lower in mock_area.lower() or mock_area.lower() in area_lower:
                return response

        # If no match found, return default with custom area name
        default = MOCK_AIR_QUALITY_DATA["Yorkshire & Humber"]
        return AirQualityResponse(
            area=area,
            max_daqi=default.max_daqi,
            summary=default.summary,
            pollutants=default.pollutants,
            forecast_date=date.today().isoformat(),
        )

    async def _fetch_from_api(
        self,
        area: Optional[str] = None,
    ) -> AirQualityResponse:
        """Fetch air quality data from external API (UK-AIR DEFRA API).

        Args:
            area: The geographic area to query.

        Returns:
            AirQualityResponse from external API.

        Raises:
            httpx.HTTPError: If the API call fails.
        """
        # UK-AIR API endpoint for daily air quality index
        # https://api.erg.ic.ac.uk/AirQuality/Information/MonitoringIndex/GroupName={GroupName}/Json
        group_name = area or "All"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/Daily/MonitoringIndex/GroupName={group_name}/Json"
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_api_response(data, area or "United Kingdom")

    def _parse_api_response(
        self, data: Dict[str, Any], area: str
    ) -> AirQualityResponse:
        """Parse raw API response into AirQualityResponse model.

        Args:
            data: Raw response data from external API.
            area: Geographic area name.

        Returns:
            Normalized AirQualityResponse.
        """
        pollutants: List[Pollutant] = []
        max_daqi = 1

        # Parse UK-AIR API response format
        daily_data = data.get("DailyAirQualityIndex", {})
        local_authority = daily_data.get("LocalAuthority", [])

        if isinstance(local_authority, list) and local_authority:
            for la in local_authority:
                site = la.get("Site", [])
                if isinstance(site, list):
                    for s in site:
                        species = s.get("Species", [])
                        if isinstance(species, list):
                            for sp in species:
                                index = int(sp.get("@AirQualityIndex", 1))
                                max_daqi = max(max_daqi, index)
                                pollutants.append(
                                    Pollutant(
                                        name=sp.get("@SpeciesCode", "Unknown"),
                                        value=float(sp.get("@Value", 0)),
                                        units="µg/m³",
                                        band=sp.get("@AirQualityBand", "Low"),
                                        index=index,
                                    )
                                )

        # Remove duplicate pollutants, keeping highest values
        unique_pollutants = self._deduplicate_pollutants(pollutants)

        return AirQualityResponse(
            area=area,
            max_daqi=max_daqi,
            summary=get_daqi_summary(max_daqi),
            pollutants=unique_pollutants,
            forecast_date=daily_data.get("@ForecastDate", date.today().isoformat()),
        )

    def _deduplicate_pollutants(
        self, pollutants: List[Pollutant]
    ) -> List[Pollutant]:
        """Remove duplicate pollutants, keeping the one with highest index.

        Args:
            pollutants: List of pollutants with potential duplicates.

        Returns:
            Deduplicated list of pollutants.
        """
        pollutant_map: Dict[str, Pollutant] = {}
        for p in pollutants:
            existing = pollutant_map.get(p.name)
            if existing is None or (p.index or 0) > (existing.index or 0):
                pollutant_map[p.name] = p
        return list(pollutant_map.values())


def get_air_quality_service(settings: Settings = None) -> AirQualityService:
    """Factory function to create AirQualityService instance.
    
    Args:
        settings: Optional settings instance. If not provided, uses default settings.
    
    Returns:
        AirQualityService instance.
    """
    if settings is None:
        settings = get_settings()
    return AirQualityService(settings)
