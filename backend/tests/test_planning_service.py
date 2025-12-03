"""
Tests for the planning service module.
"""

import pytest

from config import Settings
from models.planning import PlanningApplication, PlanningResponse
from services.cache import InMemoryCache
from services.planning_service import PlanningService


class TestPlanningService:
    """Tests for PlanningService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings(MOCK_MODE=True)
        self.cache = InMemoryCache(default_ttl=60)
        self.service = PlanningService(self.settings, cache=self.cache)

    @pytest.mark.asyncio
    async def test_get_planning_applications_returns_mock_data(self):
        """Test that mock mode returns mock data."""
        result = await self.service.get_planning_applications(lpa="York")
        
        assert isinstance(result, PlanningResponse)
        assert "York" in result.lpa
        assert len(result.applications) > 0
        assert result.total_count > 0

    @pytest.mark.asyncio
    async def test_get_planning_applications_with_date_filter(self):
        """Test filtering applications by date."""
        result = await self.service.get_planning_applications(
            lpa="York",
            date_from="2025-10-01",
            date_to="2025-11-30"
        )
        
        assert isinstance(result, PlanningResponse)
        # All applications should be within date range
        for app in result.applications:
            assert app.received_date >= "2025-10-01"
            assert app.received_date <= "2025-11-30"

    @pytest.mark.asyncio
    async def test_get_planning_applications_raises_on_missing_lpa(self):
        """Test that missing LPA raises ValueError."""
        with pytest.raises(ValueError, match="Local Planning Authority"):
            await self.service.get_planning_applications(lpa="")

    @pytest.mark.asyncio
    async def test_get_planning_applications_caches_result(self):
        """Test that results are cached."""
        # First call
        result1 = await self.service.get_planning_applications(lpa="York")
        
        # Second call should return cached data
        result2 = await self.service.get_planning_applications(lpa="York")
        
        # Should be the same object from cache
        assert result1 == result2
        assert self.cache.size() == 1

    @pytest.mark.asyncio
    async def test_get_planning_applications_different_lpas(self):
        """Test that different LPAs get different cache entries."""
        result1 = await self.service.get_planning_applications(lpa="York")
        result2 = await self.service.get_planning_applications(lpa="Manchester")
        
        # Should have two cache entries
        assert self.cache.size() == 2


class TestPlanningServiceNormalization:
    """Tests for data normalization in PlanningService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings(MOCK_MODE=True)
        self.service = PlanningService(self.settings)

    def test_normalize_status_known_statuses(self):
        """Test that known statuses are normalized correctly."""
        assert self.service._normalize_status("pending") == "Pending Consideration"
        assert self.service._normalize_status("approved") == "Approved"
        assert self.service._normalize_status("refused") == "Refused"
        assert self.service._normalize_status("withdrawn") == "Withdrawn"

    def test_normalize_status_unknown_status(self):
        """Test that unknown statuses are title-cased."""
        result = self.service._normalize_status("under review")
        assert result == "Under Review"

    def test_normalize_status_empty(self):
        """Test normalizing empty status."""
        result = self.service._normalize_status("")
        assert result == "Pending"

    def test_normalize_date_iso_format(self):
        """Test normalizing ISO date format."""
        result = self.service._normalize_date("2025-12-09")
        assert result == "2025-12-09"

    def test_normalize_date_iso_with_time(self):
        """Test normalizing ISO date with time."""
        result = self.service._normalize_date("2025-12-09T00:00:00")
        assert result == "2025-12-09"

    def test_normalize_date_empty(self):
        """Test normalizing empty date."""
        result = self.service._normalize_date("")
        assert result == ""

    def test_extract_address_direct(self):
        """Test extracting address from direct field."""
        entity = {"address": "10 Example Street, York"}
        result = self.service._extract_address(entity)
        assert result == "10 Example Street, York"

    def test_extract_address_from_name(self):
        """Test extracting address from name field with 'at'."""
        entity = {"name": "Planning Application at 10 Example Street"}
        result = self.service._extract_address(entity)
        assert "10 Example Street" in result

    def test_sort_applications_by_date(self):
        """Test that applications are sorted by date (most recent first)."""
        apps = [
            PlanningApplication(
                reference="001",
                address="Address 1",
                proposal="Proposal 1",
                status="Pending",
                received_date="2025-10-01",
            ),
            PlanningApplication(
                reference="002",
                address="Address 2",
                proposal="Proposal 2",
                status="Pending",
                received_date="2025-12-01",
            ),
            PlanningApplication(
                reference="003",
                address="Address 3",
                proposal="Proposal 3",
                status="Pending",
                received_date="2025-11-01",
            ),
        ]
        
        sorted_apps = self.service._sort_applications_by_date(apps)
        
        assert sorted_apps[0].received_date == "2025-12-01"  # Most recent first
        assert sorted_apps[1].received_date == "2025-11-01"
        assert sorted_apps[2].received_date == "2025-10-01"


class TestPlanningServiceTransformation:
    """Tests for API response transformation in PlanningService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings(MOCK_MODE=True)
        self.service = PlanningService(self.settings)

    def test_transform_planning_api_response_entities_format(self):
        """Test transforming planning.data.gov.uk response with entities format."""
        data = {
            "entities": [
                {
                    "reference": "23/12345/FUL",
                    "name": "Planning Application at 10 Example Street",
                    "entry-date": "2025-11-10",
                    "planning-decision": "pending",
                },
                {
                    "reference": "23/12346/HOU",
                    "name": "Extension at 45 Sample Street",
                    "entry-date": "2025-10-15",
                    "planning-decision": "approved",
                },
            ]
        }
        
        result = self.service._transform_planning_api_response(data, "York")
        
        assert result.lpa == "York"
        assert len(result.applications) == 2
        assert result.applications[0].reference == "23/12345/FUL"

    def test_parse_entity_complete(self):
        """Test parsing a complete entity."""
        entity = {
            "reference": "23/12345/FUL",
            "address": "10 Example Street, York",
            "description": "Erection of extension",
            "entry-date": "2025-11-10",
            "planning-decision": "approved",
            "decision-date": "2025-12-01",
            "applicant-name": "John Smith",
            "planning-application-type": "Full Application",
        }
        
        result = self.service._parse_entity(entity)
        
        assert result is not None
        assert result.reference == "23/12345/FUL"
        assert result.address == "10 Example Street, York"
        assert result.proposal == "Erection of extension"
        assert result.received_date == "2025-11-10"
        assert result.decision == "approved"
        assert result.applicant_name == "John Smith"

    def test_parse_entity_missing_reference(self):
        """Test that missing reference returns None."""
        entity = {
            "address": "10 Example Street",
            "entry-date": "2025-11-10",
        }
        
        result = self.service._parse_entity(entity)
        
        assert result is None

    def test_create_fallback_response(self):
        """Test fallback response creation."""
        result = self.service._create_fallback_response("York")
        
        assert result.lpa == "York"
        assert result.applications == []
        assert result.total_count == 0
