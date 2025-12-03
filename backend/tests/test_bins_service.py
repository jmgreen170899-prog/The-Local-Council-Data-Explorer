"""
Tests for the bins service module.
"""

import pytest

from config import Settings
from models.bins import BinCollection, BinCollectionResponse
from services.bins_service import BinsService
from services.cache import InMemoryCache


class TestBinsService:
    """Tests for BinsService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings(MOCK_MODE=True)
        self.cache = InMemoryCache(default_ttl=60)
        self.service = BinsService(self.settings, cache=self.cache)

    @pytest.mark.asyncio
    async def test_get_bin_collections_returns_mock_data(self):
        """Test that mock mode returns mock data."""
        result = await self.service.get_bin_collections(postcode="YO1 1AA")

        assert isinstance(result, BinCollectionResponse)
        assert result.council == "City of York Council"
        assert len(result.bins) > 0
        assert result.address != ""

    @pytest.mark.asyncio
    async def test_get_bin_collections_with_house_number(self):
        """Test that house number is included in address."""
        result = await self.service.get_bin_collections(
            postcode="YO1 1AA", house_number="42"
        )

        assert "42" in result.address

    @pytest.mark.asyncio
    async def test_get_bin_collections_with_uprn(self):
        """Test getting bin collections with UPRN."""
        result = await self.service.get_bin_collections(uprn="100050535540")

        assert isinstance(result, BinCollectionResponse)
        assert result.council == "City of York Council"

    @pytest.mark.asyncio
    async def test_get_bin_collections_caches_result(self):
        """Test that results are cached."""
        # First call
        result1 = await self.service.get_bin_collections(postcode="YO1 1AA")

        # Second call should return cached data
        result2 = await self.service.get_bin_collections(postcode="YO1 1AA")

        # Should be the same object from cache
        assert result1 == result2
        assert self.cache.size() == 1

    @pytest.mark.asyncio
    async def test_get_bin_collections_with_different_postcodes(self):
        """Test that different postcodes get different cache entries."""
        await self.service.get_bin_collections(postcode="SW1A 1AA")
        await self.service.get_bin_collections(postcode="M1 1AA")

        # Should have two cache entries
        assert self.cache.size() == 2


class TestBinsServiceNormalization:
    """Tests for data normalization in BinsService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings(MOCK_MODE=True)
        self.service = BinsService(self.settings)

    def test_normalize_bin_type_known_types(self):
        """Test that known bin types are normalized correctly."""
        assert self.service._normalize_bin_type("REFUSE") == "Refuse"
        assert self.service._normalize_bin_type("RECYCLING") == "Recycling"
        assert self.service._normalize_bin_type("GARDEN WASTE") == "Garden Waste"
        assert self.service._normalize_bin_type("GREY BIN") == "Refuse"
        assert self.service._normalize_bin_type("GREEN BIN") == "Recycling"

    def test_normalize_bin_type_unknown_type(self):
        """Test that unknown bin types are title-cased."""
        result = self.service._normalize_bin_type("special collection")
        assert result == "Special Collection"

    def test_normalize_date_iso_format(self):
        """Test normalizing ISO date format."""
        result = self.service._normalize_date("2025-12-09")
        assert result == "2025-12-09"

    def test_normalize_date_iso_with_time(self):
        """Test normalizing ISO date with time."""
        result = self.service._normalize_date("2025-12-09T00:00:00")
        assert result == "2025-12-09"

    def test_normalize_date_uk_format(self):
        """Test normalizing UK date format."""
        result = self.service._normalize_date("09/12/2025")
        assert result == "2025-12-09"

    def test_normalize_date_empty(self):
        """Test normalizing empty date."""
        result = self.service._normalize_date("")
        assert result == ""

    def test_sort_bins_by_date(self):
        """Test that bins are sorted by collection date."""
        bins = [
            BinCollection(type="Refuse", collection_date="2025-12-15"),
            BinCollection(type="Recycling", collection_date="2025-12-09"),
            BinCollection(type="Garden", collection_date="2025-12-12"),
        ]

        sorted_bins = self.service._sort_bins_by_date(bins)

        assert sorted_bins[0].collection_date == "2025-12-09"
        assert sorted_bins[1].collection_date == "2025-12-12"
        assert sorted_bins[2].collection_date == "2025-12-15"


class TestBinsServiceTransformation:
    """Tests for API response transformation in BinsService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings(MOCK_MODE=True)
        self.service = BinsService(self.settings)

    def test_transform_york_api_response_bins_format(self):
        """Test transforming York API response with bins format."""
        data = {
            "address": "10 Example Street, York",
            "bins": [
                {"binType": "GREY BIN", "nextCollectionDate": "2025-12-09T00:00:00"},
                {"binType": "GREEN BIN", "nextCollectionDate": "2025-12-16T00:00:00"},
            ],
        }

        result = self.service._transform_york_api_response(data, "100050535540")

        assert result.address == "10 Example Street, York"
        assert result.council == "City of York Council"
        assert len(result.bins) == 2
        assert result.bins[0].type == "Refuse"  # GREY BIN -> Refuse
        assert result.bins[0].collection_date == "2025-12-09"

    def test_transform_york_api_response_services_format(self):
        """Test transforming York API response with services format."""
        data = {
            "address": "10 Example Street, York",
            "services": [
                {"service": "REFUSE", "nextCollection": "2025-12-09T00:00:00"},
                {"service": "RECYCLING", "nextCollection": "2025-12-16T00:00:00"},
            ],
        }

        result = self.service._transform_york_api_response(data, "100050535540")

        assert result.address == "10 Example Street, York"
        assert len(result.bins) == 2
        assert result.bins[0].type == "Refuse"

    def test_create_fallback_response(self):
        """Test fallback response creation."""
        result = self.service._create_fallback_response(
            postcode="YO1 1AA", house_number="10"
        )

        assert "10" in result.address
        assert "YO1 1AA" in result.address
        assert result.council == "City of York Council"
        assert result.bins == []
