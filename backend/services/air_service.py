"""
Air quality service module.

This module contains business logic for air quality data retrieval and processing.

Implements async HTTP calls using httpx to the UK-AIR / Defra API.
The API endpoint is: https://api.erg.ic.ac.uk/AirQuality

Data Flow:
1. Request comes in with an area/region name
2. Check cache for existing data
3. If not cached, fetch from UK-AIR Defra API
4. Transform raw JSON response into internal AirQualityResponse model
5. Cache the result for future requests (short TTL as air quality changes)
6. Return normalized response

Transformation Details:
- The UK-AIR API returns data in the following structure:
  - "DailyAirQualityIndex": Contains forecast data
    - "LocalAuthority": Array of local authority data
      - Each has "Site": Array of monitoring sites
        - Each site has "Species": Array of pollutant measurements
- We transform this into our internal model which has:
  - area: Geographic area name
  - max_daqi: Maximum Daily Air Quality Index (1-10)
  - summary: Quality band (Low, Moderate, High, Very High)
  - pollutants: List of individual pollutant measurements

Fallback Behavior:
- If API returns empty/null fields, we provide sensible defaults
- If API is unavailable, cached data is returned if available
- If no data available, returns default "Low" quality with empty pollutants

Uses the UK Daily Air Quality Index (DAQI) scale from 1-10.
"""

import logging
from datetime import date
from typing import Any, Dict, List, Optional

import httpx

from config import Settings, get_settings
from models.air_quality import AirQualityResponse, Pollutant
from services.cache import get_air_quality_cache, InMemoryCache

logger = logging.getLogger(__name__)


# DAQI band definitions based on UK Air Quality Index
DAQI_BANDS = {
    (1, 3): "Low",
    (4, 6): "Moderate",
    (7, 9): "High",
    (10, 10): "Very High",
}


def get_daqi_summary(index: int) -> str:
    """Get DAQI summary text for a given index value.

    The UK Daily Air Quality Index ranges from 1-10:
    - 1-3: Low pollution - Enjoy your usual outdoor activities
    - 4-6: Moderate pollution - Consider reducing strenuous activities
    - 7-9: High pollution - Reduce strenuous activities outdoors
    - 10: Very High pollution - Avoid strenuous activities outdoors

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
            Pollutant(
                name="PM2.5", value=18.5, units="µg/m³", band="Moderate", index=4
            ),
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

# Mapping of UK-AIR species codes to user-friendly pollutant names
POLLUTANT_NAME_MAPPING: Dict[str, str] = {
    "NO2": "Nitrogen Dioxide (NO₂)",
    "O3": "Ozone (O₃)",
    "PM10": "PM₁₀ Particles",
    "PM2.5": "PM₂.₅ Fine Particles",
    "PM25": "PM₂.₅ Fine Particles",
    "SO2": "Sulphur Dioxide (SO₂)",
    "CO": "Carbon Monoxide (CO)",
}


class AirQualityService:
    """Service for retrieving air quality data from UK-AIR Defra API.

    This service wraps the UK-AIR API (https://api.erg.ic.ac.uk/AirQuality)
    and transforms the response into our internal data model.

    The UK Daily Air Quality Index (DAQI) is used to provide health advice:
    - 1-3: Low pollution
    - 4-6: Moderate pollution
    - 7-9: High pollution
    - 10: Very High pollution

    Attributes:
        settings: Application settings instance.
        base_url: Base URL for the UK-AIR API.
        timeout: HTTP timeout configuration.
        cache: In-memory cache for air quality data.
    """

    def __init__(self, settings: Settings, cache: Optional[InMemoryCache] = None):
        """Initialize the air quality service.

        Args:
            settings: Application settings instance.
            cache: Optional cache instance. If not provided, uses global cache.
        """
        self.settings = settings
        self.base_url = settings.AIR_QUALITY_API_BASE_URL
        self.timeout = httpx.Timeout(
            timeout=settings.HTTP_TIMEOUT,
            connect=settings.HTTP_CONNECT_TIMEOUT,
        )
        self.cache = cache or get_air_quality_cache()

    async def get_air_quality(
        self,
        area: Optional[str] = None,
    ) -> AirQualityResponse:
        """Retrieve air quality data for a given area.

        This method first checks the cache for existing data. If not found,
        it fetches from the UK-AIR API and caches the result.

        Args:
            area: The geographic area to get air quality data for.
                  If not provided, defaults to "Yorkshire & Humber".

        Returns:
            AirQualityResponse containing DAQI index, summary, and pollutant breakdown.

        Raises:
            httpx.HTTPError: If the external API call fails.
        """
        # Default area if not provided
        if not area:
            area = "Yorkshire & Humber"

        # Generate cache key based on input parameters
        cache_key = self.cache.generate_key("air_quality", area=area)

        # Check cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"Returning cached air quality data for key: {cache_key}")
            return cached

        if self.settings.MOCK_MODE:
            result = self._get_mock_data(area)
        else:
            result = await self._fetch_from_api(area)

        # Cache the result with short TTL (air quality changes frequently)
        self.cache.set(cache_key, result, ttl=self.settings.CACHE_TTL_AIR_QUALITY)
        return result

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
        """Fetch air quality data from UK-AIR Defra API.

        The API endpoint format is:
        GET https://api.erg.ic.ac.uk/AirQuality/Daily/MonitoringIndex/GroupName={GroupName}/Json

        Alternative endpoint for forecasts:
        GET https://api.erg.ic.ac.uk/AirQuality/Forecast/MonitoringIndex/GroupName={GroupName}/Json

        Args:
            area: The geographic area to query. Used as GroupName parameter.

        Returns:
            AirQualityResponse from external API.

        Raises:
            httpx.HTTPError: If the API call fails.
        """
        # Use "All" to get nationwide data if no specific area
        group_name = area or "All"

        # Build the API URL for UK-AIR daily monitoring index
        # Try the daily monitoring index first
        url = f"{self.base_url}/Daily/MonitoringIndex/GroupName={group_name}/Json"

        logger.info(f"Fetching air quality data from: {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            return self._transform_ukair_api_response(data, area or "United Kingdom")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from UK-AIR API: {e}")
            # Try fallback to forecast endpoint
            return await self._fetch_forecast_fallback(area)
        except httpx.RequestError as e:
            logger.error(f"Request error connecting to UK-AIR API: {e}")
            raise

    async def _fetch_forecast_fallback(
        self, area: Optional[str] = None
    ) -> AirQualityResponse:
        """Fallback to forecast endpoint if daily monitoring fails.

        Args:
            area: The geographic area to query.

        Returns:
            AirQualityResponse from forecast API or default fallback.
        """
        group_name = area or "All"
        url = f"{self.base_url}/Forecast/MonitoringIndex/GroupName={group_name}/Json"

        logger.info(f"Trying forecast fallback: {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            return self._transform_ukair_api_response(data, area or "United Kingdom")

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.warning(f"Forecast fallback also failed: {e}")
            return self._create_fallback_response(area or "United Kingdom")

    def _transform_ukair_api_response(self, data: Any, area: str) -> AirQualityResponse:
        """Transform UK-AIR API response into internal model.

        The UK-AIR API returns data in the following structure:
        {
            "DailyAirQualityIndex": {
                "@ForecastDate": "2025-12-03",
                "LocalAuthority": [
                    {
                        "@LocalAuthorityName": "York",
                        "Site": [
                            {
                                "@SiteName": "York Fishergate",
                                "Species": [
                                    {
                                        "@SpeciesCode": "NO2",
                                        "@AirQualityIndex": "2",
                                        "@AirQualityBand": "Low",
                                        "@Value": "18.5"
                                    },
                                    ...
                                ]
                            },
                            ...
                        ]
                    },
                    ...
                ]
            }
        }

        Args:
            data: Raw JSON response from UK-AIR API.
            area: Geographic area name for the response.

        Returns:
            Normalized AirQualityResponse.
        """
        pollutants: List[Pollutant] = []
        max_daqi = 1
        forecast_date = date.today().isoformat()

        # Handle different response formats
        if not isinstance(data, dict):
            logger.warning(f"Unexpected API response type: {type(data)}")
            return self._create_fallback_response(area)

        # Parse UK-AIR API response format
        daily_data = data.get("DailyAirQualityIndex", {})

        # Extract forecast date if available
        forecast_date = daily_data.get("@ForecastDate", forecast_date)

        # Get local authority data
        local_authority = daily_data.get("LocalAuthority", [])

        # Ensure it's a list
        if isinstance(local_authority, dict):
            local_authority = [local_authority]

        if isinstance(local_authority, list) and local_authority:
            for la in local_authority:
                if not isinstance(la, dict):
                    continue

                # Get sites from this local authority
                site = la.get("Site", [])

                # Ensure it's a list
                if isinstance(site, dict):
                    site = [site]

                if isinstance(site, list):
                    for s in site:
                        if not isinstance(s, dict):
                            continue

                        # Get species (pollutant) measurements
                        species = s.get("Species", [])

                        # Ensure it's a list
                        if isinstance(species, dict):
                            species = [species]

                        if isinstance(species, list):
                            for sp in species:
                                if not isinstance(sp, dict):
                                    continue

                                pollutant = self._parse_species(sp)
                                if pollutant:
                                    # Track max DAQI
                                    if pollutant.index and pollutant.index > max_daqi:
                                        max_daqi = pollutant.index
                                    pollutants.append(pollutant)

        # Remove duplicate pollutants, keeping highest values
        unique_pollutants = self._deduplicate_pollutants(pollutants)

        # Recalculate max_daqi from deduplicated pollutants
        if unique_pollutants:
            max_daqi = max((p.index or 1 for p in unique_pollutants), default=1)

        return AirQualityResponse(
            area=area,
            max_daqi=max_daqi,
            summary=get_daqi_summary(max_daqi),
            pollutants=unique_pollutants,
            forecast_date=forecast_date,
        )

    def _parse_species(self, sp: Dict[str, Any]) -> Optional[Pollutant]:
        """Parse a single species (pollutant) from UK-AIR API response.

        The species data has the following format:
        {
            "@SpeciesCode": "NO2",
            "@AirQualityIndex": "2",
            "@AirQualityBand": "Low",
            "@Value": "18.5"
        }

        Args:
            sp: Species data from API response.

        Returns:
            Pollutant object if parsing succeeds, None otherwise.
        """
        try:
            # Extract species code (pollutant name)
            species_code = sp.get("@SpeciesCode", "Unknown")

            # Get the measured value
            value_str = sp.get("@Value", "0")
            try:
                value = float(value_str) if value_str else 0.0
            except (ValueError, TypeError):
                value = 0.0

            # Get DAQI index
            index_str = sp.get("@AirQualityIndex", "1")
            try:
                index = int(index_str) if index_str else 1
                # Ensure index is within valid range
                index = max(1, min(10, index))
            except (ValueError, TypeError):
                index = 1

            # Get quality band
            band = sp.get("@AirQualityBand", get_daqi_summary(index))

            return Pollutant(
                name=species_code,
                value=value,
                units="µg/m³",  # Standard units for air quality
                band=band,
                index=index,
            )

        except Exception as e:
            logger.warning(f"Error parsing species data: {e}")
            return None

    def _deduplicate_pollutants(self, pollutants: List[Pollutant]) -> List[Pollutant]:
        """Remove duplicate pollutants, keeping the one with highest index.

        When multiple readings exist for the same pollutant (from different
        monitoring sites), we keep the worst reading (highest index) as a
        conservative measure.

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

        # Sort pollutants by index (worst first) for clarity
        sorted_pollutants = sorted(
            pollutant_map.values(), key=lambda x: x.index or 0, reverse=True
        )
        return sorted_pollutants

    def _create_fallback_response(self, area: str) -> AirQualityResponse:
        """Create a fallback response when API data is unavailable.

        This provides a graceful degradation when the upstream API
        cannot provide data.

        Args:
            area: Geographic area name.

        Returns:
            AirQualityResponse with default values.
        """
        return AirQualityResponse(
            area=area,
            max_daqi=1,  # Assume low if unknown
            summary="Low",
            pollutants=[],  # Empty pollutants indicates no data
            forecast_date=date.today().isoformat(),
        )


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
