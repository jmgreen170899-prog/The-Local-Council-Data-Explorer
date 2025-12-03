"""
Tests for the API routers.

These tests verify the HTTP endpoints return correct responses
and handle errors appropriately.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from config import Settings


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_returns_ok(self, client):
        """Test that /health returns status ok."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_root_returns_api_info(self, client):
        """Test that / returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "docs" in data
        assert data["docs"] == "/docs"


class TestBinsEndpoint:
    """Tests for the /api/bins endpoint."""

    def test_bins_requires_postcode_or_uprn(self, client):
        """Test that endpoint requires at least postcode or uprn."""
        response = client.get("/api/bins")
        
        assert response.status_code == 400
        data = response.json()
        assert "postcode" in data["detail"].lower() or "uprn" in data["detail"].lower()

    def test_bins_with_postcode_returns_data(self, client):
        """Test getting bins with a postcode."""
        response = client.get("/api/bins?postcode=YO1%201AA")
        
        assert response.status_code == 200
        data = response.json()
        assert "address" in data
        assert "council" in data
        assert "bins" in data
        assert isinstance(data["bins"], list)

    def test_bins_with_uprn_returns_data(self, client):
        """Test getting bins with a UPRN."""
        response = client.get("/api/bins?uprn=100050535540")
        
        assert response.status_code == 200
        data = response.json()
        assert "address" in data
        assert "council" in data

    def test_bins_with_house_number(self, client):
        """Test getting bins with postcode and house number."""
        response = client.get("/api/bins?postcode=YO1%201AA&house_number=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "10" in data["address"]


class TestPlanningEndpoint:
    """Tests for the /api/planning endpoint."""

    def test_planning_requires_lpa(self, client):
        """Test that endpoint requires LPA parameter."""
        response = client.get("/api/planning")
        
        # FastAPI returns 422 for missing required query params
        assert response.status_code == 422

    def test_planning_with_lpa_returns_data(self, client):
        """Test getting planning data with LPA."""
        response = client.get("/api/planning?lpa=City%20of%20York%20Council")
        
        assert response.status_code == 200
        data = response.json()
        assert "lpa" in data
        assert "applications" in data
        assert "total_count" in data
        assert isinstance(data["applications"], list)

    def test_planning_with_date_range(self, client):
        """Test planning with date filters."""
        response = client.get(
            "/api/planning?lpa=City%20of%20York%20Council"
            "&date_from=2025-01-01&date_to=2025-12-31"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data

    def test_planning_invalid_date_range(self, client):
        """Test that invalid date range is rejected."""
        response = client.get(
            "/api/planning?lpa=Test"
            "&date_from=2025-12-31&date_to=2025-01-01"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "date" in data["detail"].lower()

    def test_planning_invalid_date_format(self, client):
        """Test that invalid date format is rejected."""
        response = client.get(
            "/api/planning?lpa=Test&date_from=invalid-date"
        )
        
        # FastAPI validates the pattern
        assert response.status_code == 422


class TestAirQualityEndpoint:
    """Tests for the /api/air-quality endpoint."""

    def test_air_quality_without_area_returns_default(self, client):
        """Test getting air quality without specifying area."""
        response = client.get("/api/air-quality")
        
        assert response.status_code == 200
        data = response.json()
        assert "area" in data
        assert "max_daqi" in data
        assert "summary" in data
        assert "pollutants" in data

    def test_air_quality_with_area(self, client):
        """Test getting air quality for specific area."""
        response = client.get("/api/air-quality?area=Greater%20London")
        
        assert response.status_code == 200
        data = response.json()
        assert data["area"] == "Greater London"
        assert data["max_daqi"] >= 1
        assert data["max_daqi"] <= 10

    def test_air_quality_response_structure(self, client):
        """Test that air quality response has correct structure."""
        response = client.get("/api/air-quality")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "area" in data
        assert "max_daqi" in data
        assert "summary" in data
        assert "pollutants" in data
        assert "forecast_date" in data
        
        # Check pollutant structure if present
        if data["pollutants"]:
            pollutant = data["pollutants"][0]
            assert "name" in pollutant
            assert "value" in pollutant
            assert "units" in pollutant


class TestCORSHeaders:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.options(
            "/api/bins",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        
        # FastAPI CORS middleware should respond
        assert response.status_code in [200, 204]


class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation endpoints."""

    def test_openapi_json_available(self, client):
        """Test that OpenAPI JSON is available."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "/api/bins" in str(data["paths"])

    def test_swagger_ui_available(self, client):
        """Test that Swagger UI is available."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    def test_redoc_available(self, client):
        """Test that ReDoc is available."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
