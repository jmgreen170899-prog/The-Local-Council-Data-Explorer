"""
Bins service module.

This module contains business logic for bin collection data retrieval and processing.
Implements async HTTP calls using httpx and provides mock data for offline development.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

from config import Settings, get_settings
from models.bins import BinCollection, BinCollectionResponse

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


class BinsService:
    """Service for retrieving bin collection data."""

    def __init__(self, settings: Settings):
        """Initialize the bins service.
        
        Args:
            settings: Application settings instance.
        """
        self.settings = settings
        self.base_url = settings.BINS_API_BASE_URL
        self.timeout = httpx.Timeout(
            timeout=settings.HTTP_TIMEOUT,
            connect=settings.HTTP_CONNECT_TIMEOUT,
        )

    async def get_bin_collections(
        self,
        postcode: Optional[str] = None,
        house_number: Optional[str] = None,
        uprn: Optional[str] = None,
    ) -> BinCollectionResponse:
        """Retrieve bin collection data for a given location.

        Args:
            postcode: The postcode to look up bin collections for.
            house_number: The house number or name.
            uprn: The Unique Property Reference Number.

        Returns:
            BinCollectionResponse containing address, council, and bin collection details.

        Raises:
            httpx.HTTPError: If the external API call fails.
            ValueError: If neither postcode+house_number nor uprn is provided.
        """
        if self.settings.MOCK_MODE:
            return self._get_mock_data(postcode, house_number, uprn)

        return await self._fetch_from_api(postcode, house_number, uprn)

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
        """Fetch bin collection data from external API.

        Args:
            postcode: The postcode to look up.
            house_number: The house number or name.
            uprn: The Unique Property Reference Number.

        Returns:
            BinCollectionResponse from external API.

        Raises:
            httpx.HTTPError: If the API call fails.
        """
        params: Dict[str, Any] = {}
        if uprn:
            params["uprn"] = uprn
        elif postcode:
            params["postcode"] = postcode
            if house_number:
                params["house_number"] = house_number

        headers = {}
        if self.settings.BINS_API_KEY:
            headers["Authorization"] = f"Bearer {self.settings.BINS_API_KEY}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                self.base_url,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_api_response(data)

    def _parse_api_response(self, data: Dict[str, Any]) -> BinCollectionResponse:
        """Parse raw API response into BinCollectionResponse model.

        Args:
            data: Raw response data from external API.

        Returns:
            Normalized BinCollectionResponse.
        """
        bins: List[BinCollection] = []
        raw_bins = data.get("bins", data.get("collections", []))

        for bin_item in raw_bins:
            bins.append(
                BinCollection(
                    type=bin_item.get("type", bin_item.get("bin_type", "Unknown")),
                    collection_date=bin_item.get(
                        "collection_date", bin_item.get("next_collection", "")
                    ),
                )
            )

        return BinCollectionResponse(
            address=data.get("address", data.get("property_address", "")),
            council=data.get("council", data.get("local_authority", "")),
            bins=bins,
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
