# Architecture

This document provides a comprehensive overview of the system architecture, design patterns, and technical decisions for the Local Council Data Explorer.

## Table of Contents

- [System Overview](#system-overview)
- [High-Level Architecture](#high-level-architecture)
- [Technology Stack](#technology-stack)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Data Flow](#data-flow)
- [Caching Strategy](#caching-strategy)
- [External API Integration](#external-api-integration)
- [Error Handling Strategy](#error-handling-strategy)
- [Security Considerations](#security-considerations)
- [Design Decisions](#design-decisions)
- [Future Considerations](#future-considerations)

---

## System Overview

The Local Council Data Explorer is a full-stack web application that aggregates and visualizes local council data from multiple UK government APIs. The system follows a client-server architecture with a clear separation between the presentation layer (React frontend) and the business logic layer (FastAPI backend).

### Core Objectives

1. **Data Aggregation** – Consolidate data from disparate council APIs into a unified interface
2. **Performance** – Minimize latency through intelligent caching and async operations
3. **Resilience** – Graceful degradation when external services are unavailable
4. **Developer Experience** – Mock mode for offline development and testing

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT TIER                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         React Application                              │  │
│  │  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────────┐    │  │
│  │  │   Layout    │  │     Features    │  │       Components        │    │  │
│  │  │  Component  │  │ (bins/planning/ │  │   (Card, Charts, etc.)  │    │  │
│  │  │             │  │   air quality)  │  │                         │    │  │
│  │  └─────────────┘  └─────────────────┘  └─────────────────────────┘    │  │
│  │                              │                                         │  │
│  │  ┌───────────────────────────▼────────────────────────────────────┐   │  │
│  │  │                        Hooks (useApi)                          │   │  │
│  │  │        Async state management with loading/error handling      │   │  │
│  │  └────────────────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                       │
│                                      │ HTTP/REST (JSON)                      │
└──────────────────────────────────────┼───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              SERVER TIER                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                         FastAPI Application                            │  │
│  │                                                                        │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │  │
│  │  │                        Routers Layer                              │ │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │ │  │
│  │  │  │ bins.py     │  │ planning.py │  │     air_quality.py      │   │ │  │
│  │  │  │ /api/bins   │  │/api/planning│  │    /api/air-quality     │   │ │  │
│  │  │  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘   │ │  │
│  │  └─────────┼────────────────┼──────────────────────┼────────────────┘ │  │
│  │            │                │                      │                   │  │
│  │  ┌─────────▼────────────────▼──────────────────────▼────────────────┐ │  │
│  │  │                      Services Layer                              │ │  │
│  │  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐ │ │  │
│  │  │  │  bins_service   │ │planning_service │ │   air_service       │ │ │  │
│  │  │  │ - fetch/cache   │ │ - fetch/cache   │ │  - fetch/cache      │ │ │  │
│  │  │  │ - transform     │ │ - transform     │ │  - transform        │ │ │  │
│  │  │  │ - mock support  │ │ - mock support  │ │  - mock support     │ │ │  │
│  │  │  └─────────────────┘ └─────────────────┘ └─────────────────────┘ │ │  │
│  │  └──────────────────────────────┬───────────────────────────────────┘ │  │
│  │                                 │                                      │  │
│  │  ┌──────────────────────────────▼───────────────────────────────────┐ │  │
│  │  │                      Caching Layer                               │ │  │
│  │  │          InMemoryCache with TTL-based expiration                 │ │  │
│  │  └──────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                        │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │  │
│  │  │                       Models Layer                                │ │  │
│  │  │         Pydantic schemas for validation & serialization          │ │  │
│  │  └──────────────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
┌─────────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│    EXTERNAL APIS        │ │   EXTERNAL APIS     │ │   EXTERNAL APIS     │
│                         │ │                     │ │                     │
│   City of York          │ │   planning.data     │ │     UK-AIR          │
│   Waste API             │ │    .gov.uk          │ │   Defra API         │
│                         │ │                     │ │                     │
│   Bin collection        │ │   Planning          │ │   Air quality       │
│   schedules             │ │   applications      │ │   measurements      │
└─────────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

---

## Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Runtime** | Python | 3.11+ | Server-side programming language |
| **Framework** | FastAPI | Latest | Async web framework with automatic API docs |
| **Validation** | Pydantic | v2 | Data validation and settings management |
| **HTTP Client** | httpx | Latest | Async HTTP client for external APIs |
| **Server** | Uvicorn | Latest | ASGI server for production |
| **Configuration** | pydantic-settings | Latest | Environment-based configuration |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Runtime** | Node.js | 20+ | JavaScript runtime for build tools |
| **Framework** | React | 19 | Component-based UI library |
| **Language** | TypeScript | 5.9+ | Type-safe JavaScript |
| **Build Tool** | Vite | Latest | Fast bundler and dev server |
| **Charting** | Recharts | 3.x | Declarative chart components |
| **Linting** | ESLint | 9.x | Code quality enforcement |

---

## Backend Architecture

### Directory Structure

```
backend/
├── main.py                     # Application entry point
├── config.py                   # Settings and configuration
├── routers/                    # HTTP route handlers
│   ├── __init__.py
│   ├── bins.py                 # /api/bins endpoint
│   ├── planning.py             # /api/planning endpoint
│   └── air_quality.py          # /api/air-quality endpoint
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── bins_service.py         # Bin collection data processing
│   ├── planning_service.py     # Planning data processing
│   ├── air_service.py          # Air quality data processing
│   └── cache.py                # In-memory caching implementation
├── models/                     # Pydantic data models
│   ├── __init__.py
│   ├── bins.py                 # Bin collection schemas
│   ├── planning.py             # Planning application schemas
│   ├── air_quality.py          # Air quality schemas
│   └── errors.py               # Error response schemas
└── tests/                      # Unit and integration tests
    ├── __init__.py
    ├── test_bins_service.py
    ├── test_planning_service.py
    ├── test_air_service.py
    └── test_cache.py
```

### Layer Responsibilities

#### Routers Layer
- HTTP request/response handling
- Input validation via FastAPI Query parameters
- Dependency injection of services
- Error response mapping
- OpenAPI documentation annotations

#### Services Layer
- Business logic encapsulation
- External API communication
- Data transformation and normalization
- Cache management
- Mock data provision for development

#### Models Layer
- Request/response schema definitions
- Pydantic validation rules
- Automatic serialization
- OpenAPI schema generation

#### Caching Layer
- Thread-safe in-memory storage
- Configurable TTL per data type
- Lazy expiration on access
- Cache key generation helpers

---

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── main.tsx                # Application bootstrap
│   ├── App.tsx                 # Root component with routing
│   ├── App.css                 # Global styles
│   ├── index.css               # Base styles
│   ├── components/             # Shared UI components
│   │   ├── Card.tsx            # Container component
│   │   ├── ChartWrapper.tsx    # Chart display wrapper
│   │   └── Layout.tsx          # Page layout with navigation
│   ├── features/               # Domain-specific modules
│   │   ├── bins/
│   │   │   ├── BinPanel.tsx    # Bin collections UI
│   │   │   ├── api.ts          # API functions
│   │   │   └── types.ts        # TypeScript types
│   │   ├── planning/
│   │   │   ├── PlanningPanel.tsx
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   └── air/
│   │       ├── AirQualityPanel.tsx
│   │       ├── api.ts
│   │       └── types.ts
│   ├── hooks/                  # Custom React hooks
│   │   └── useApi.ts           # Async data fetching hook
│   └── assets/                 # Static assets
├── public/                     # Static files
├── index.html                  # HTML entry point
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies and scripts
```

### Component Architecture

#### Feature Modules
Each feature (bins, planning, air) follows the same pattern:
- **Panel Component** – Main UI for the feature
- **API Module** – HTTP functions with retry logic
- **Types Module** – TypeScript interfaces mirroring backend models

#### Shared Components
- **Layout** – Navigation and page structure
- **Card** – Consistent container styling
- **ChartWrapper** – Responsive chart containers

#### Custom Hooks
- **useApi** – Manages async state (loading, error, data) with refetch capability

---

## Data Flow

### Request Flow (Frontend → Backend → External API)

```
1. User Action (e.g., load bin collections)
        │
        ▼
2. React Component calls Feature API function
        │
        ▼
3. API function makes HTTP request to backend
        │
        ▼
4. FastAPI Router receives request
        │
        ▼
5. Router calls Service (via dependency injection)
        │
        ▼
6. Service checks cache
        │
        ├── Cache HIT → Return cached data
        │
        └── Cache MISS → Fetch from external API
                │
                ▼
7. External API response received
        │
        ▼
8. Service transforms data to internal model
        │
        ▼
9. Service caches result with TTL
        │
        ▼
10. Router returns JSON response
        │
        ▼
11. Frontend updates UI with new data
```

### Data Transformation Pipeline

```
External API Response
        │
        ▼
┌───────────────────────────────────────┐
│    Service Transformation Logic       │
│  - Field mapping (snake_case etc.)    │
│  - Date normalization (ISO format)    │
│  - Type conversion                    │
│  - Null/default handling              │
│  - Sorting and filtering              │
└───────────────────────────────────────┘
        │
        ▼
Internal Pydantic Model
        │
        ▼
JSON Serialization
        │
        ▼
Frontend TypeScript Type
```

---

## Caching Strategy

### Cache Configuration

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| **Bin Collections** | 1 hour | Schedules rarely change within a day |
| **Planning Applications** | 30 minutes | Status updates can occur throughout the day |
| **Air Quality** | 10 minutes | Real-time data, changes frequently |

### Cache Implementation

The `InMemoryCache` class provides:

```python
class InMemoryCache:
    """Thread-safe in-memory cache with TTL support."""
    
    def get(self, key: str) -> Optional[Any]  # Retrieve if not expired
    def set(self, key: str, value: Any, ttl: int)  # Store with TTL
    def delete(self, key: str) -> bool  # Manual invalidation
    def cleanup() -> int  # Remove expired entries
```

### Cache Key Generation

Cache keys are generated from request parameters:

```
bins:postcode=YO1 1AA
planning:lpa=City of York Council:date_from=2025-01-01
air_quality:area=Yorkshire & Humber
```

---

## External API Integration

### City of York Waste API (Bin Collections)

| Attribute | Value |
|-----------|-------|
| **Base URL** | `https://waste-api.york.gov.uk/api/Collections` |
| **Authentication** | None required |
| **Endpoint** | `GET /GetBinCollectionDataForUprn/{UPRN}` |
| **Response Format** | JSON with `bins` array |

### planning.data.gov.uk (Planning Applications)

| Attribute | Value |
|-----------|-------|
| **Base URL** | `https://www.planning.data.gov.uk` |
| **Authentication** | None required |
| **Endpoint** | `GET /entity.json` |
| **Query Parameters** | `dataset`, `limit`, `entry_date_*` |

### UK-AIR Defra API (Air Quality)

| Attribute | Value |
|-----------|-------|
| **Base URL** | `https://api.erg.ic.ac.uk/AirQuality` |
| **Authentication** | None required |
| **Endpoint** | `GET /Daily/MonitoringIndex/GroupName={area}/Json` |
| **Fallback** | `GET /Forecast/MonitoringIndex/GroupName={area}/Json` |

---

## Error Handling Strategy

### Backend Error Handling

```python
# Router-level error mapping
try:
    result = await service.get_data(...)
    return result
except httpx.TimeoutException:
    raise HTTPException(503, "External service timed out")
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        raise HTTPException(404, "Resource not found")
    raise HTTPException(503, "External service error")
except ValueError as e:
    raise HTTPException(400, str(e))
except Exception:
    raise HTTPException(500, "Unexpected error")
```

### Frontend Error Handling

```typescript
// useApi hook manages error state
const { data, loading, error, refetch } = useApi(fetcher);

// Components display error UI with retry
if (error) {
  return <ErrorState message={error} onRetry={refetch} />;
}
```

### Error Response Format

```json
{
  "detail": "Human-readable error message",
  "code": "OPTIONAL_ERROR_CODE"
}
```

---

## Security Considerations

### Current Implementation

1. **Input Validation** – All inputs validated via Pydantic/FastAPI
2. **No Authentication** – Public read-only API (appropriate for open data)
3. **CORS** – Not configured (add for production cross-origin access)
4. **Rate Limiting** – Not implemented (consider for production)

### Recommended Production Additions

1. **CORS Configuration** – Restrict origins to known frontend domains
2. **Rate Limiting** – Prevent API abuse (e.g., 100 requests/minute)
3. **Request Logging** – Audit trail for API access
4. **HTTPS Only** – Enforce TLS in production
5. **API Versioning** – URL-based versioning (`/api/v1/...`)

---

## Design Decisions

### Why FastAPI?

| Benefit | Explanation |
|---------|-------------|
| **Performance** | Async support for non-blocking I/O with external APIs |
| **Type Safety** | Pydantic integration for automatic validation |
| **Documentation** | Auto-generated OpenAPI/Swagger docs |
| **Developer Experience** | Intuitive decorator-based API definition |

### Why React + TypeScript?

| Benefit | Explanation |
|---------|-------------|
| **Component Model** | Reusable, composable UI components |
| **Type Safety** | Compile-time error detection |
| **Ecosystem** | Large library ecosystem (Recharts, etc.) |
| **Vite** | Fast development iteration with HMR |

### Why Feature-Based Frontend Structure?

| Benefit | Explanation |
|---------|-------------|
| **Cohesion** | Related code lives together |
| **Scalability** | Add features without touching existing code |
| **Maintainability** | Clear ownership of each module |
| **Testing** | Feature modules can be tested in isolation |

### Why In-Memory Caching?

| Benefit | Explanation |
|---------|-------------|
| **Simplicity** | No external dependencies (Redis, etc.) |
| **Performance** | Fastest possible cache reads |
| **Suitable Scale** | Appropriate for single-instance deployment |
| **Trade-off** | Cache lost on restart (acceptable for this use case) |

---

## Future Considerations

### Short-Term Enhancements

1. **Database Layer** – Add SQLite/PostgreSQL for persistent caching
2. **Docker Support** – Containerize for consistent deployments
3. **CI/CD Pipeline** – Automated testing and deployment
4. **Additional Councils** – Expand beyond City of York

### Medium-Term Enhancements

1. **User Accounts** – Save favorite postcodes/LPAs
2. **Notifications** – Email/SMS alerts for bin collections
3. **Real-Time Updates** – WebSocket for live air quality data
4. **Mobile App** – React Native companion app

### Long-Term Enhancements

1. **Multi-Region** – Deploy to multiple regions for redundancy
2. **Data Analytics** – Historical trends and insights
3. **API Gateway** – Kong/AWS API Gateway for advanced management
4. **Machine Learning** – Predict bin collection disruptions

---

## Related Documentation

- [README.md](./README.md) – Project overview and quick start
- [SYSTEM_FLOW.md](./SYSTEM_FLOW.md) – Sequence diagrams and data flows
- [API_REFERENCE.md](./API_REFERENCE.md) – Detailed API documentation
