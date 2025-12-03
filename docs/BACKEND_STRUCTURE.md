# Backend Structure

> A detailed guide to the FastAPI backend architecture, module organization, and implementation patterns.

---

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Module Breakdown](#module-breakdown)
- [Layer Architecture](#layer-architecture)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Best Practices](#best-practices)

---

## Overview

The backend is built with **FastAPI**, a modern, high-performance Python web framework. It follows a layered architecture pattern that separates concerns and promotes testability.

### Key Characteristics

| Feature | Implementation |
|---------|----------------|
| **Framework** | FastAPI with async/await |
| **Data Validation** | Pydantic v2 models |
| **Configuration** | pydantic-settings with `.env` support |
| **HTTP Client** | httpx for async external API calls |
| **Caching** | Thread-safe in-memory TTL cache |
| **Testing** | pytest with pytest-asyncio |

---

## Directory Structure

```
backend/
├── main.py                     # Application entry point & FastAPI app
├── config.py                   # Settings and configuration
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build instructions
│
├── routers/                    # HTTP route handlers
│   ├── __init__.py
│   ├── bins.py                 # /api/bins endpoint
│   ├── planning.py             # /api/planning endpoint
│   └── air_quality.py          # /api/air-quality endpoint
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── bins_service.py         # Bin collection data processing
│   ├── planning_service.py     # Planning data processing
│   ├── air_service.py          # Air quality data processing
│   └── cache.py                # In-memory caching implementation
│
├── models/                     # Pydantic data models
│   ├── __init__.py
│   ├── bins.py                 # Bin collection schemas
│   ├── planning.py             # Planning application schemas
│   ├── air_quality.py          # Air quality schemas
│   └── errors.py               # Error response schemas
│
└── tests/                      # Test suite
    ├── __init__.py
    ├── test_bins_service.py
    ├── test_planning_service.py
    ├── test_air_service.py
    ├── test_cache.py
    └── test_routers.py
```

---

## Module Breakdown

### `main.py` - Application Entry Point

The main module creates and configures the FastAPI application:

```python
# Key responsibilities:
# 1. Create FastAPI app with metadata
# 2. Configure CORS middleware
# 3. Include routers with prefixes
# 4. Define health check endpoints

app = FastAPI(
    title="Local Council Data Explorer API",
    version=settings.API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, ...)
app.include_router(bins.router, prefix="/api")
app.include_router(planning.router, prefix="/api")
app.include_router(air_quality.router, prefix="/api")
```

### `config.py` - Configuration Management

Centralized configuration using pydantic-settings:

```python
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )
    
    # Application settings
    APP_NAME: str = "Local Council Data Explorer"
    DEBUG: bool = Field(default=False)
    MOCK_MODE: bool = Field(default=True)
    
    # External API URLs
    BINS_API_BASE_URL: str = "..."
    PLANNING_API_BASE_URL: str = "..."
    AIR_QUALITY_API_BASE_URL: str = "..."
    
    # Cache TTLs (seconds)
    CACHE_TTL_BINS: int = 3600
    CACHE_TTL_PLANNING: int = 1800
    CACHE_TTL_AIR_QUALITY: int = 600
```

### Routers Layer

Each router handles a specific domain:

| Router | Prefix | Endpoints |
|--------|--------|-----------|
| `bins.py` | `/bins` | `GET /api/bins` |
| `planning.py` | `/planning` | `GET /api/planning` |
| `air_quality.py` | `/air-quality` | `GET /api/air-quality` |

**Router Pattern:**

```python
from fastapi import APIRouter, Query, HTTPException
from services.bins_service import BinsService
from models.bins import BinCollectionResponse

router = APIRouter(prefix="/bins")
service = BinsService()

@router.get("", response_model=BinCollectionResponse)
async def get_bin_collections(
    postcode: Optional[str] = Query(None),
    uprn: Optional[str] = Query(None),
) -> BinCollectionResponse:
    """Get bin collection schedule for a property."""
    if not postcode and not uprn:
        raise HTTPException(400, "Either 'postcode' or 'uprn' required")
    
    return await service.get_bin_collections(postcode, uprn)
```

### Services Layer

Services encapsulate business logic and external API integration:

**Service Responsibilities:**

1. **Cache Management**: Check/update cache before external calls
2. **External API Calls**: Fetch data with timeout and retry
3. **Data Transformation**: Convert external formats to internal models
4. **Mock Data**: Return realistic data in development mode
5. **Error Handling**: Handle failures gracefully

**Service Pattern:**

```python
class BinsService:
    """Service for fetching and processing bin collection data."""
    
    def __init__(self) -> None:
        self._cache = InMemoryCache()
        self._client = httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT)
    
    async def get_bin_collections(
        self, 
        postcode: Optional[str], 
        uprn: Optional[str]
    ) -> BinCollectionResponse:
        """Get bin collections with caching."""
        cache_key = self._cache.generate_key("bins", postcode=postcode, uprn=uprn)
        
        # Check cache
        cached = self._cache.get(cache_key)
        if cached:
            return cached
        
        # Fetch from API or mock
        if settings.MOCK_MODE:
            result = self._get_mock_data(postcode)
        else:
            result = await self._fetch_from_api(postcode, uprn)
        
        # Cache and return
        self._cache.set(cache_key, result, settings.CACHE_TTL_BINS)
        return result
```

### Models Layer

Pydantic models define request/response schemas:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class BinCollection(BaseModel):
    """Single bin collection schedule."""
    type: str = Field(..., description="Bin type (Refuse, Recycling, etc.)")
    collection_date: date = Field(..., description="Next collection date")

class BinCollectionResponse(BaseModel):
    """Response model for bin collection data."""
    address: str = Field(..., description="Property address")
    council: str = Field(..., description="Council name")
    bins: List[BinCollection] = Field(default_factory=list)
```

### Cache Module

Thread-safe in-memory cache with TTL:

```python
@dataclass
class CacheEntry:
    """Single cache entry with expiration."""
    value: Any
    expires_at: float
    created_at: float
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

class InMemoryCache:
    """Thread-safe in-memory cache with TTL support."""
    
    def __init__(self) -> None:
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value if exists and not expired."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self._cache[key]
                return None
            return entry.value
    
    def set(self, key: str, value: Any, ttl: int) -> None:
        """Store value with TTL."""
        with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                expires_at=time.time() + ttl,
                created_at=time.time(),
            )
```

---

## Layer Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         Routers Layer                          │
│   • HTTP request/response handling                             │
│   • Input validation via FastAPI Query parameters              │
│   • OpenAPI documentation annotations                          │
│   • Error response mapping                                     │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                        Services Layer                          │
│   • Business logic encapsulation                               │
│   • External API communication                                 │
│   • Data transformation and normalization                      │
│   • Cache management                                           │
│   • Mock data provision                                        │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                         Models Layer                           │
│   • Request/response schema definitions                        │
│   • Pydantic validation rules                                  │
│   • Automatic serialization                                    │
│   • OpenAPI schema generation                                  │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                        Caching Layer                           │
│   • Thread-safe storage                                        │
│   • Configurable TTL per data type                             │
│   • Lazy expiration on access                                  │
│   • Cache key generation helpers                               │
└────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEBUG` | bool | `false` | Enable debug logging |
| `MOCK_MODE` | bool | `true` | Use mock data instead of external APIs |
| `API_VERSION` | str | `v1` | API version string |
| `BINS_API_BASE_URL` | str | (set) | York Waste API URL |
| `PLANNING_API_BASE_URL` | str | (set) | Planning API URL |
| `AIR_QUALITY_API_BASE_URL` | str | (set) | UK-AIR API URL |
| `CACHE_TTL_BINS` | int | `3600` | Bin data cache TTL (seconds) |
| `CACHE_TTL_PLANNING` | int | `1800` | Planning data cache TTL (seconds) |
| `CACHE_TTL_AIR_QUALITY` | int | `600` | Air quality data cache TTL (seconds) |
| `HTTP_TIMEOUT` | float | `30.0` | HTTP request timeout (seconds) |
| `HTTP_MAX_RETRIES` | int | `3` | Maximum retry attempts |

### Configuration Loading Priority

1. Environment variables (highest priority)
2. `.env` file
3. Default values in `Settings` class

---

## Error Handling

### Exception Hierarchy

```
Exception
├── HTTPException (FastAPI)
│   ├── 400 Bad Request - Invalid input
│   ├── 404 Not Found - Resource not found
│   ├── 422 Unprocessable Entity - Validation error
│   ├── 500 Internal Server Error - Unexpected error
│   └── 503 Service Unavailable - External API failure
│
└── httpx exceptions
    ├── TimeoutException → 503
    ├── HTTPStatusError → 503 or fallback
    └── RequestError → 503
```

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### Router Error Handling Pattern

```python
@router.get("")
async def get_data(...):
    try:
        return await service.get_data(...)
    except httpx.TimeoutException:
        raise HTTPException(503, "External service timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(404, "Resource not found")
        raise HTTPException(503, "External service error")
    except ValueError as e:
        raise HTTPException(400, str(e))
```

---

## Testing

### Test Structure

```
tests/
├── test_bins_service.py      # Bin service unit tests
├── test_planning_service.py  # Planning service unit tests
├── test_air_service.py       # Air quality service unit tests
├── test_cache.py             # Cache functionality tests
└── test_routers.py           # API endpoint integration tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_bins_service.py

# Run with verbose output
pytest -v
```

### Test Patterns

**Service Tests:**

```python
import pytest
from services.bins_service import BinsService

@pytest.fixture
def service():
    return BinsService()

@pytest.mark.asyncio
async def test_get_mock_bin_collections(service):
    """Test mock data retrieval."""
    result = await service.get_bin_collections("YO1 1AA", None)
    assert result.council == "City of York Council"
    assert len(result.bins) > 0
```

**Router Tests:**

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_bins_endpoint():
    """Test bins API endpoint."""
    response = client.get("/api/bins?postcode=YO1%201AA")
    assert response.status_code == 200
    assert "bins" in response.json()
```

---

## Best Practices

### Code Organization

1. **One router per domain** - bins, planning, air quality
2. **Service per router** - encapsulate business logic
3. **Models mirror API responses** - clear schema definitions
4. **Shared cache instance** - avoid duplicate caching

### Type Hints

All functions should have complete type hints:

```python
async def get_bin_collections(
    self,
    postcode: Optional[str],
    uprn: Optional[str],
) -> BinCollectionResponse:
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def get_bin_collections(self, postcode: str) -> BinCollectionResponse:
    """Get bin collection schedule for a property.
    
    Args:
        postcode: UK postcode for the property.
    
    Returns:
        BinCollectionResponse containing collection schedule.
    
    Raises:
        HTTPException: If external API fails.
    """
```

### Async Best Practices

1. **Use async throughout** - don't block the event loop
2. **httpx for HTTP calls** - async HTTP client
3. **Avoid sync operations** - file I/O, database calls should be async
4. **Proper timeout handling** - always set timeouts

---

## Related Documentation

- [Architecture Overview](./ARCHITECTURE_OVERVIEW.md) - High-level system architecture
- [Frontend Structure](./FRONTEND_STRUCTURE.md) - Frontend component architecture
- [API Reference](../API_REFERENCE.md) - Complete API documentation
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions
