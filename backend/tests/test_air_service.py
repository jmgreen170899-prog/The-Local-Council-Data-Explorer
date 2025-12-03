"""
Tests for the air quality service module.
"""

import pytest

from config import Settings
from models.air_quality import AirQualityResponse, Pollutant
from services.air_service import AirQualityService, get_daqi_summary
from services.cache import InMemoryCache


class TestDaqiSummary:
    """Tests for DAQI summary function."""

    def test_low_index(self):
        """Test DAQI indexes 1-3 return Low."""
        assert get_daqi_summary(1) == "Low"
        assert get_daqi_summary(2) == "Low"
        assert get_daqi_summary(3) == "Low"

    def test_moderate_index(self):
        """Test DAQI indexes 4-6 return Moderate."""
        assert get_daqi_summary(4) == "Moderate"
        assert get_daqi_summary(5) == "Moderate"
        assert get_daqi_summary(6) == "Moderate"

    def test_high_index(self):
        """Test DAQI indexes 7-9 return High."""
        assert get_daqi_summary(7) == "High"
        assert get_daqi_summary(8) == "High"
        assert get_daqi_summary(9) == "High"

    def test_very_high_index(self):
        """Test DAQI index 10 returns Very High."""
        assert get_daqi_summary(10) == "Very High"

    def test_invalid_index(self):
        """Test invalid index returns Unknown."""
        assert get_daqi_summary(0) == "Unknown"
        assert get_daqi_summary(11) == "Unknown"


class TestAirQualityService:
    """Tests for AirQualityService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings(MOCK_MODE=True)
        self.cache = InMemoryCache(default_ttl=60)
        self.service = AirQualityService(self.settings, cache=self.cache)

    @pytest.mark.asyncio
    async def test_get_air_quality_returns_mock_data(self):
        """Test that mock mode returns mock data."""
        result = await self.service.get_air_quality(area="Yorkshire")

        assert isinstance(result, AirQualityResponse)
        assert "Yorkshire" in result.area
        assert 1 <= result.max_daqi <= 10
        assert result.summary in ["Low", "Moderate", "High", "Very High"]
        assert len(result.pollutants) > 0

    @pytest.mark.asyncio
    async def test_get_air_quality_default_area(self):
        """Test that default area is used when not provided."""
        result = await self.service.get_air_quality()

        assert isinstance(result, AirQualityResponse)
        assert result.area == "Yorkshire & Humber"

    @pytest.mark.asyncio
    async def test_get_air_quality_london(self):
        """Test getting air quality for London."""
        result = await self.service.get_air_quality(area="London")

        assert "London" in result.area
        # London mock data has moderate air quality
        assert result.summary == "Moderate"

    @pytest.mark.asyncio
    async def test_get_air_quality_caches_result(self):
        """Test that results are cached."""
        # First call
        result1 = await self.service.get_air_quality(area="Yorkshire")

        # Second call should return cached data
        result2 = await self.service.get_air_quality(area="Yorkshire")

        # Should be the same object from cache
        assert result1 == result2
        assert self.cache.size() == 1

    @pytest.mark.asyncio
    async def test_get_air_quality_different_areas(self):
        """Test that different areas get different cache entries."""
        await self.service.get_air_quality(area="Yorkshire")
        await self.service.get_air_quality(area="London")

        # Should have two cache entries
        assert self.cache.size() == 2


class TestAirQualityServiceTransformation:
    """Tests for API response transformation in AirQualityService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings(MOCK_MODE=True)
        self.service = AirQualityService(self.settings)

    def test_transform_ukair_api_response_standard_format(self):
        """Test transforming UK-AIR API response with standard format."""
        data = {
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
                                        "@Value": "18.5",
                                    },
                                    {
                                        "@SpeciesCode": "PM2.5",
                                        "@AirQualityIndex": "3",
                                        "@AirQualityBand": "Low",
                                        "@Value": "10.0",
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        }

        result = self.service._transform_ukair_api_response(data, "Yorkshire")

        assert result.area == "Yorkshire"
        assert result.max_daqi == 3  # Highest index from pollutants
        assert result.summary == "Low"
        assert result.forecast_date == "2025-12-03"
        assert len(result.pollutants) == 2

    def test_transform_ukair_api_response_single_site(self):
        """Test transforming response with single site (dict instead of list)."""
        data = {
            "DailyAirQualityIndex": {
                "@ForecastDate": "2025-12-03",
                "LocalAuthority": {
                    "@LocalAuthorityName": "York",
                    "Site": {
                        "@SiteName": "York Fishergate",
                        "Species": {
                            "@SpeciesCode": "NO2",
                            "@AirQualityIndex": "2",
                            "@AirQualityBand": "Low",
                            "@Value": "18.5",
                        },
                    },
                },
            }
        }

        result = self.service._transform_ukair_api_response(data, "Yorkshire")

        assert result.area == "Yorkshire"
        assert len(result.pollutants) == 1
        assert result.pollutants[0].name == "NO2"

    def test_parse_species_complete(self):
        """Test parsing a complete species entry."""
        species = {
            "@SpeciesCode": "NO2",
            "@AirQualityIndex": "4",
            "@AirQualityBand": "Moderate",
            "@Value": "42.5",
        }

        result = self.service._parse_species(species)

        assert result is not None
        assert result.name == "NO2"
        assert result.value == 42.5
        assert result.index == 4
        assert result.band == "Moderate"
        assert result.units == "µg/m³"

    def test_parse_species_missing_values(self):
        """Test parsing species with missing values uses defaults."""
        species = {
            "@SpeciesCode": "O3",
        }

        result = self.service._parse_species(species)

        assert result is not None
        assert result.name == "O3"
        assert result.value == 0.0
        assert result.index == 1
        assert result.band == "Low"

    def test_deduplicate_pollutants_keeps_highest(self):
        """Test that deduplication keeps pollutant with highest index."""
        pollutants = [
            Pollutant(name="NO2", value=18.0, units="µg/m³", band="Low", index=2),
            Pollutant(name="NO2", value=35.0, units="µg/m³", band="Moderate", index=4),
            Pollutant(name="PM2.5", value=10.0, units="µg/m³", band="Low", index=2),
        ]

        result = self.service._deduplicate_pollutants(pollutants)

        # Should have 2 unique pollutants
        assert len(result) == 2

        # NO2 should have the higher index
        no2 = next(p for p in result if p.name == "NO2")
        assert no2.index == 4
        assert no2.value == 35.0

    def test_create_fallback_response(self):
        """Test fallback response creation."""
        result = self.service._create_fallback_response("Unknown Area")

        assert result.area == "Unknown Area"
        assert result.max_daqi == 1
        assert result.summary == "Low"
        assert result.pollutants == []
        assert result.forecast_date is not None


class TestAirQualityServicePollutants:
    """Tests for pollutant handling in AirQualityService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings(MOCK_MODE=True)
        self.service = AirQualityService(self.settings)

    @pytest.mark.asyncio
    async def test_pollutants_have_required_fields(self):
        """Test that all pollutants have required fields."""
        result = await self.service.get_air_quality(area="London")

        for pollutant in result.pollutants:
            assert pollutant.name is not None
            assert pollutant.value is not None
            assert pollutant.units is not None
            assert pollutant.index is not None
            assert 1 <= pollutant.index <= 10

    @pytest.mark.asyncio
    async def test_max_daqi_matches_highest_pollutant(self):
        """Test that max_daqi matches the highest pollutant index."""
        result = await self.service.get_air_quality(area="London")

        if result.pollutants:
            # Use explicit null checking for pollutant indices (DAQI ranges 1-10)
            highest_index = max(
                p.index if p.index is not None else 1 for p in result.pollutants
            )
            assert result.max_daqi == highest_index
