"""
Bins service module.

This module contains business logic for bin collection data retrieval and processing.

Implements async HTTP calls using httpx to the City of York Council Waste Collection API.
The API endpoint is: https://waste-api.york.gov.uk/api/Collections/GetBinCollectionDataForUprn/{UPRN}

Data Flow:
1. Request comes in with UPRN or postcode+house_number
2. Check cache for existing data
3. If not cached, fetch from City of York Waste API
4. Transform raw JSON response into internal BinCollectionResponse model
5. Cache the result for future requests
6. Return normalized response

Transformation Details:
- The City of York API returns bin collection data with fields like:
  - "services": array of bin collection services
  - Each service has: "service", "round", "schedule", "nextCollection", etc.
- We transform this into our internal model which has:
  - address: Full property address
  - council: Always "City of York Council"
  - bins: List of BinCollection with type and collection_date

Fallback Behavior:
- If API returns empty/null fields, we provide sensible defaults
- If API is unavailable, cached data is returned if available
- If no data available, returns empty bins list with generic message
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from config import Settings, get_settings
from models.bins import BinCollection, BinCollectionResponse
from services.cache import get_bins_cache, InMemoryCache

logger = logging.getLogger(__name__)


# Mock data for offline/local development
MOCK_BIN_DATA: Dict[str, BinCollectionResponse] = {
    "default": BinCollectionResponse(
        address="10 Example Street, York, YO1 1AA",
        council="City of York Council",
        bins=[
            BinCollection(type="Refuse", collection_date="2025-12-09"),
            BinCollection(type="Recycling", collection_date="2025-12-16"),
            BinCollection(type="Garden Waste", collection_date="2025-12-23"),
        ],
    ),
    "SW1A1AA": BinCollectionResponse(
        address="10 Downing Street, London, SW1A 1AA",
        council="Westminster City Council",
        bins=[
            BinCollection(type="General Waste", collection_date="2025-12-10"),
            BinCollection(type="Recycling", collection_date="2025-12-12"),
            BinCollection(type="Food Waste", collection_date="2025-12-10"),
        ],
    ),
    "M11AA": BinCollectionResponse(
        address="1 Piccadilly Gardens, Manchester, M1 1AA",
        council="Manchester City Council",
        bins=[
            BinCollection(type="Black Bin", collection_date="2025-12-11"),
            BinCollection(type="Blue Bin", collection_date="2025-12-18"),
        ],
    ),
}

# Mapping of City of York API service names to user-friendly bin types
BIN_TYPE_MAPPING: Dict[str, str] = {
    "REFUSE": "Refuse",
    "RECYCLING": "Recycling",
    "GARDEN": "Garden Waste",
    "GARDEN WASTE": "Garden Waste",
    "FOOD": "Food Waste",
    "KERBSIDE RECYCLING": "Recycling",
    "GREY BIN": "Refuse",
    "GREEN BIN": "Recycling",
    "BROWN BIN": "Garden Waste",
}


class BinsService:
    """Service for retrieving bin collection data from City of York Council API.
    
    This service wraps the City of York Council Waste Collection Lookup API
    (https://waste-api.york.gov.uk/api/Collections) and transforms the response
    into our internal data model.
    
    Attributes:
        settings: Application settings instance.
        base_url: Base URL for the City of York API.
        timeout: HTTP timeout configuration.
        cache: In-memory cache for bin collection data.
    """

    def __init__(self, settings: Settings, cache: Optional[InMemoryCache] = None):
        """Initialize the bins service.
        
        Args:
            settings: Application settings instance.
            cache: Optional cache instance. If not provided, uses global cache.
        """
        self.settings = settings
        self.base_url = settings.BINS_API_BASE_URL
        self.timeout = httpx.Timeout(
            timeout=settings.HTTP_TIMEOUT,
            connect=settings.HTTP_CONNECT_TIMEOUT,
        )
        self.cache = cache or get_bins_cache()

    async def get_bin_collections(
        self,
        postcode: Optional[str] = None,
        house_number: Optional[str] = None,
        uprn: Optional[str] = None,
    ) -> BinCollectionResponse:
        """Retrieve bin collection data for a given location.
        
        This method first checks the cache for existing data. If not found,
        it fetches from the City of York API and caches the result.

        Args:
            postcode: The postcode to look up bin collections for.
            house_number: The house number or name.
            uprn: The Unique Property Reference Number (preferred lookup method).

        Returns:
            BinCollectionResponse containing address, council, and bin collection details.

        Raises:
            httpx.HTTPError: If the external API call fails and no cached data available.
            ValueError: If neither postcode+house_number nor uprn is provided.
        """
        # Generate cache key based on input parameters
        cache_key = self.cache.generate_key("bins", uprn=uprn, postcode=postcode)
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"Returning cached bin collection data for key: {cache_key}")
            return cached

        if self.settings.MOCK_MODE:
            result = self._get_mock_data(postcode, house_number, uprn)
        else:
            result = await self._fetch_from_api(postcode, house_number, uprn)
        
        # Cache the result
        self.cache.set(cache_key, result, ttl=self.settings.CACHE_TTL_BINS)
        return result

    def _get_mock_data(
        self,
        postcode: Optional[str] = None,
        house_number: Optional[str] = None,
        uprn: Optional[str] = None,
    ) -> BinCollectionResponse:
        """Get mock bin collection data for development.

        Args:
            postcode: The postcode to look up.
            house_number: The house number or name.
            uprn: The Unique Property Reference Number.

        Returns:
            Mock BinCollectionResponse data.
        """
        logger.info("Using mock data for bin collections")

        # Normalize postcode for lookup
        if postcode:
            normalized_postcode = postcode.upper().replace(" ", "")
            if normalized_postcode in MOCK_BIN_DATA:
                response = MOCK_BIN_DATA[normalized_postcode]
                # Update address with house number if provided
                if house_number:
                    response = BinCollectionResponse(
                        address=f"{house_number}, {response.address}",
                        council=response.council,
                        bins=response.bins,
                    )
                return response

        # Return default mock data
        default_response = MOCK_BIN_DATA["default"]
        if house_number:
            return BinCollectionResponse(
                address=f"{house_number} Example Street, York, YO1 1AA",
                council=default_response.council,
                bins=default_response.bins,
            )
        return default_response

    async def _fetch_from_api(
        self,
        postcode: Optional[str] = None,
        house_number: Optional[str] = None,
        uprn: Optional[str] = None,
    ) -> BinCollectionResponse:
        """Fetch bin collection data from City of York Council Waste API.
        
        The API endpoint format is:
        GET https://waste-api.york.gov.uk/api/Collections/GetBinCollectionDataForUprn/{UPRN}

        Args:
            postcode: The postcode to look up (not directly supported by API).
            house_number: The house number or name (not directly supported by API).
            uprn: The Unique Property Reference Number (required for API lookup).

        Returns:
            BinCollectionResponse from external API.

        Raises:
            httpx.HTTPError: If the API call fails.
            ValueError: If UPRN is not provided.
        """
        # City of York API requires UPRN for lookup
        if not uprn:
            # If no UPRN provided, return fallback response
            # In a production system, we would need a UPRN lookup service
            logger.warning("No UPRN provided, returning fallback data")
            return self._create_fallback_response(postcode, house_number)

        # Build the API URL for City of York Waste Collection API
        url = f"{self.base_url}/GetBinCollectionDataForUprn/{uprn}"
        
        logger.info(f"Fetching bin collection data from: {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            return self._transform_york_api_response(data, uprn)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from City of York API: {e}")
            # Return fallback on 404 (UPRN not found)
            if e.response.status_code == 404:
                return self._create_fallback_response(postcode, house_number, uprn)
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error connecting to City of York API: {e}")
            raise

    def _transform_york_api_response(
        self, data: Any, uprn: str
    ) -> BinCollectionResponse:
        """Transform City of York API response into internal model.
        
        The City of York API returns data in the following structure:
        {
            "bins": [
                {
                    "binType": "GREY BIN",
                    "binTypeDescription": "Rubbish collection",
                    "nextCollectionDate": "2025-12-09T00:00:00"
                },
                ...
            ]
        }
        
        Or in some cases:
        {
            "services": [
                {
                    "service": "REFUSE",
                    "nextCollection": "2025-12-09T00:00:00",
                    "schedule": "Fortnightly"
                },
                ...
            ],
            "address": "10 Example Street, York"
        }

        Args:
            data: Raw JSON response from City of York API.
            uprn: The UPRN used for the lookup.

        Returns:
            Normalized BinCollectionResponse.
        """
        bins: List[BinCollection] = []
        address = "Unknown Address"
        
        # Handle different response formats from the API
        if isinstance(data, dict):
            # Extract address if available
            address = data.get("address", data.get("propertyAddress", f"UPRN: {uprn}"))
            
            # Check for "bins" array format
            raw_bins = data.get("bins", [])
            if raw_bins:
                bins = self._parse_bins_array(raw_bins)
            
            # Check for "services" array format  
            services = data.get("services", [])
            if services:
                bins = self._parse_services_array(services)
                
            # Check for direct collection arrays
            collections = data.get("collections", [])
            if collections:
                bins = self._parse_collections_array(collections)
                
        elif isinstance(data, list):
            # If the response is directly a list of bins
            bins = self._parse_bins_array(data)
        
        # Sort bins by collection date
        bins = self._sort_bins_by_date(bins)
        
        return BinCollectionResponse(
            address=address,
            council="City of York Council",
            bins=bins,
        )

    def _parse_bins_array(self, raw_bins: List[Dict[str, Any]]) -> List[BinCollection]:
        """Parse bins array from City of York API response.
        
        Handles the format:
        {
            "binType": "GREY BIN",
            "binTypeDescription": "Rubbish collection", 
            "nextCollectionDate": "2025-12-09T00:00:00"
        }

        Args:
            raw_bins: List of bin objects from API.

        Returns:
            List of BinCollection objects.
        """
        bins: List[BinCollection] = []
        
        for bin_item in raw_bins:
            # Get bin type - check multiple possible field names
            bin_type = (
                bin_item.get("binType")
                or bin_item.get("bin_type")
                or bin_item.get("type")
                or bin_item.get("binTypeDescription")
                or "Unknown"
            )
            
            # Normalize bin type using mapping
            normalized_type = self._normalize_bin_type(bin_type)
            
            # Get collection date - check multiple possible field names
            collection_date = (
                bin_item.get("nextCollectionDate")
                or bin_item.get("next_collection_date")
                or bin_item.get("collectionDate")
                or bin_item.get("date")
                or ""
            )
            
            # Parse and normalize the date
            normalized_date = self._normalize_date(collection_date)
            
            if normalized_date:  # Only add if we have a valid date
                bins.append(
                    BinCollection(
                        type=normalized_type,
                        collection_date=normalized_date,
                    )
                )
        
        return bins

    def _parse_services_array(
        self, services: List[Dict[str, Any]]
    ) -> List[BinCollection]:
        """Parse services array from City of York API response.
        
        Handles the format:
        {
            "service": "REFUSE",
            "nextCollection": "2025-12-09T00:00:00",
            "schedule": "Fortnightly"
        }

        Args:
            services: List of service objects from API.

        Returns:
            List of BinCollection objects.
        """
        bins: List[BinCollection] = []
        
        for service in services:
            service_type = (
                service.get("service")
                or service.get("serviceType")
                or service.get("type")
                or "Unknown"
            )
            
            normalized_type = self._normalize_bin_type(service_type)
            
            collection_date = (
                service.get("nextCollection")
                or service.get("next_collection")
                or service.get("collectionDate")
                or ""
            )
            
            normalized_date = self._normalize_date(collection_date)
            
            if normalized_date:
                bins.append(
                    BinCollection(
                        type=normalized_type,
                        collection_date=normalized_date,
                    )
                )
        
        return bins

    def _parse_collections_array(
        self, collections: List[Dict[str, Any]]
    ) -> List[BinCollection]:
        """Parse generic collections array from API response.

        Args:
            collections: List of collection objects from API.

        Returns:
            List of BinCollection objects.
        """
        bins: List[BinCollection] = []
        
        for coll in collections:
            coll_type = (
                coll.get("type")
                or coll.get("binType")
                or coll.get("service")
                or "Unknown"
            )
            
            normalized_type = self._normalize_bin_type(coll_type)
            
            collection_date = (
                coll.get("collection_date")
                or coll.get("date")
                or coll.get("nextCollection")
                or ""
            )
            
            normalized_date = self._normalize_date(collection_date)
            
            if normalized_date:
                bins.append(
                    BinCollection(
                        type=normalized_type,
                        collection_date=normalized_date,
                    )
                )
        
        return bins

    def _normalize_bin_type(self, bin_type: str) -> str:
        """Normalize bin type to user-friendly name.
        
        Maps API-specific bin type names to consistent, user-friendly names.

        Args:
            bin_type: Raw bin type from API.

        Returns:
            Normalized bin type string.
        """
        # Convert to uppercase for lookup
        upper_type = bin_type.upper().strip()
        
        # Check mapping
        if upper_type in BIN_TYPE_MAPPING:
            return BIN_TYPE_MAPPING[upper_type]
        
        # Return title case of original if no mapping found
        return bin_type.strip().title()

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to ISO format (YYYY-MM-DD).
        
        Handles various date formats from the API:
        - ISO format: "2025-12-09T00:00:00"
        - Date only: "2025-12-09"
        - UK format: "09/12/2025"

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
            "%Y-%m-%dT%H:%M:%S",  # ISO with time
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO with milliseconds
            "%Y-%m-%d",  # ISO date only
            "%d/%m/%Y",  # UK format
            "%d-%m-%Y",  # UK format with dashes
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return date_str  # Return original if parsing fails

    def _sort_bins_by_date(
        self, bins: List[BinCollection]
    ) -> List[BinCollection]:
        """Sort bins by collection date, earliest first.

        Args:
            bins: List of BinCollection objects.

        Returns:
            Sorted list of BinCollection objects.
        """
        def parse_date(bin_item: BinCollection) -> datetime:
            try:
                return datetime.strptime(bin_item.collection_date, "%Y-%m-%d")
            except ValueError:
                return datetime.max

        return sorted(bins, key=parse_date)

    def _create_fallback_response(
        self,
        postcode: Optional[str] = None,
        house_number: Optional[str] = None,
        uprn: Optional[str] = None,
    ) -> BinCollectionResponse:
        """Create a fallback response when API data is unavailable.
        
        This provides a graceful degradation when the upstream API
        cannot provide data.

        Args:
            postcode: The postcode if provided.
            house_number: The house number if provided.
            uprn: The UPRN if provided.

        Returns:
            BinCollectionResponse with empty bins and informative address.
        """
        address_parts = []
        if house_number:
            address_parts.append(house_number)
        if postcode:
            address_parts.append(postcode)
        if uprn:
            address_parts.append(f"(UPRN: {uprn})")
        
        address = ", ".join(address_parts) if address_parts else "Unknown Address"
        
        return BinCollectionResponse(
            address=address,
            council="City of York Council",
            bins=[],  # Empty bins list indicates no data available
        )


def get_bins_service(settings: Settings = None) -> BinsService:
    """Factory function to create BinsService instance.
    
    Args:
        settings: Optional settings instance. If not provided, uses default settings.
    
    Returns:
        BinsService instance.
    """
    if settings is None:
        settings = get_settings()
    return BinsService(settings)
