# API Reference

This document provides a comprehensive reference for all API endpoints in the Local Council Data Explorer backend.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Bin Collections](#bin-collections)
  - [Planning Applications](#planning-applications)
  - [Air Quality](#air-quality)
- [Data Models](#data-models)
- [Rate Limiting](#rate-limiting)
- [OpenAPI Specification](#openapi-specification)

---

## Overview

The Local Council Data Explorer API is a RESTful API built with FastAPI. It provides endpoints for retrieving UK local council data including bin collection schedules, planning applications, and air quality information.

### Key Features

- **Automatic Documentation** – OpenAPI/Swagger UI available at `/docs`
- **JSON Responses** – All endpoints return JSON
- **Caching** – Responses are cached to reduce external API load
- **Mock Mode** – Development mode with mock data (no external dependencies)

---

## Base URL

| Environment | Base URL |
|-------------|----------|
| **Local Development** | `http://localhost:8000` |
| **Production** | `https://your-api-domain.com` |

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible for read operations.

> **Note:** For production deployments, consider implementing API key authentication or OAuth2.

---

## Response Format

### Successful Response

All successful responses return JSON with the following HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| `200 OK` | Request successful |

### Response Headers

```http
Content-Type: application/json
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### HTTP Status Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| `400 Bad Request` | Invalid request parameters | Missing required fields, invalid date format |
| `404 Not Found` | Resource not found | No data for given postcode/LPA |
| `500 Internal Server Error` | Unexpected server error | Unhandled exception |
| `503 Service Unavailable` | External service unavailable | External API timeout or error |

### Error Examples

**400 Bad Request:**
```json
{
  "detail": "Either 'postcode' or 'uprn' must be provided"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "External bin collection service timed out"
}
```

---

## Endpoints

### Health Check

Check if the API is running and healthy.

#### `GET /health`

**Description:** Returns the health status of the API.

**Parameters:** None

**Response:**

```json
{
  "status": "ok"
}
```

**Example Request:**

```bash
curl http://localhost:8000/health
```

---

### Bin Collections

Retrieve bin collection schedules for a property.

#### `GET /api/bins`

**Description:** Get bin collection schedule for a property. Provide either postcode + house_number, or UPRN.

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `postcode` | string | Conditional | UK postcode for the property | `YO1 1AA` |
| `house_number` | string | Optional | House number or name | `10` |
| `uprn` | string | Conditional | Unique Property Reference Number | `100070123456` |

> **Note:** Either `postcode` or `uprn` must be provided.

**Response Model:** [BinCollectionResponse](#bincollectionresponse)

**Success Response (200 OK):**

```json
{
  "address": "10 Example Street, York, YO1 1AA",
  "council": "City of York Council",
  "bins": [
    {
      "type": "Refuse",
      "collection_date": "2025-12-09"
    },
    {
      "type": "Recycling",
      "collection_date": "2025-12-16"
    },
    {
      "type": "Garden Waste",
      "collection_date": "2025-12-23"
    }
  ]
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `400` | Missing postcode or uprn |
| `404` | No bin collection data found for address |
| `503` | External service unavailable or timed out |

**Example Requests:**

```bash
# By postcode
curl "http://localhost:8000/api/bins?postcode=YO1%201AA"

# By postcode with house number
curl "http://localhost:8000/api/bins?postcode=YO1%201AA&house_number=10"

# By UPRN
curl "http://localhost:8000/api/bins?uprn=100070123456"
```

---

### Planning Applications

Retrieve planning applications for a Local Planning Authority.

#### `GET /api/planning`

**Description:** Get planning applications for a local planning authority. Optionally filter by date range.

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `lpa` | string | **Required** | Local Planning Authority name or identifier | `City of York Council` |
| `date_from` | string | Optional | Start date for filtering (YYYY-MM-DD) | `2025-01-01` |
| `date_to` | string | Optional | End date for filtering (YYYY-MM-DD) | `2025-12-31` |

**Response Model:** [PlanningResponse](#planningresponse)

**Success Response (200 OK):**

```json
{
  "lpa": "City of York Council",
  "applications": [
    {
      "reference": "23/12345/FUL",
      "address": "12 Example Road, York, YO1 1AB",
      "proposal": "Erection of single storey rear extension",
      "status": "Pending Consideration",
      "received_date": "2025-11-10",
      "decision_date": null,
      "decision": null,
      "applicant_name": null,
      "application_type": "Full Application"
    },
    {
      "reference": "23/12346/HOU",
      "address": "45 Sample Street, York, YO2 2CD",
      "proposal": "Loft conversion with rear dormer window",
      "status": "Approved",
      "received_date": "2025-10-15",
      "decision_date": "2025-11-20",
      "decision": "Approved",
      "applicant_name": null,
      "application_type": "Householder"
    }
  ],
  "total_count": 2
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `400` | Invalid date format or date_from > date_to |
| `404` | No planning data found for LPA |
| `503` | External service unavailable or timed out |

**Example Requests:**

```bash
# Basic query
curl "http://localhost:8000/api/planning?lpa=City%20of%20York%20Council"

# With date range
curl "http://localhost:8000/api/planning?lpa=City%20of%20York%20Council&date_from=2025-01-01&date_to=2025-12-31"
```

---

### Air Quality

Retrieve air quality data and DAQI index for a geographic area.

#### `GET /api/air-quality`

**Description:** Get current air quality data and DAQI (Daily Air Quality Index) for an area. If no area is specified, returns data for the default region (Yorkshire & Humber).

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `area` | string | Optional | Geographic area or region to query | `Greater London` |

**Response Model:** [AirQualityResponse](#airqualityresponse)

**Success Response (200 OK):**

```json
{
  "area": "Greater London",
  "max_daqi": 4,
  "summary": "Moderate",
  "pollutants": [
    {
      "name": "PM2.5",
      "value": 18.5,
      "units": "µg/m³",
      "band": "Moderate",
      "index": 4
    },
    {
      "name": "NO2",
      "value": 42.0,
      "units": "µg/m³",
      "band": "Moderate",
      "index": 3
    },
    {
      "name": "O3",
      "value": 52.0,
      "units": "µg/m³",
      "band": "Low",
      "index": 2
    },
    {
      "name": "PM10",
      "value": 28.3,
      "units": "µg/m³",
      "band": "Low",
      "index": 2
    }
  ],
  "forecast_date": "2025-12-03"
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `503` | External service unavailable or timed out |
| `500` | Unexpected error |

**DAQI Bands Reference:**

| Index Range | Band | Health Advice |
|-------------|------|---------------|
| 1-3 | Low | Enjoy your usual outdoor activities |
| 4-6 | Moderate | Consider reducing strenuous activities |
| 7-9 | High | Reduce strenuous activities outdoors |
| 10 | Very High | Avoid strenuous activities outdoors |

**Example Requests:**

```bash
# Default area (Yorkshire & Humber)
curl "http://localhost:8000/api/air-quality"

# Specific area
curl "http://localhost:8000/api/air-quality?area=Greater%20London"
```

---

## Data Models

### BinCollectionResponse

Response model for bin collection data.

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | Full address of the property |
| `council` | string | Name of the local council |
| `bins` | array[[BinCollection](#bincollection)] | List of bin collection schedules |

### BinCollection

Model for a single bin collection.

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Type of bin (e.g., Refuse, Recycling, Garden) |
| `collection_date` | string | Next collection date (YYYY-MM-DD) |

### PlanningResponse

Response model for planning applications.

| Field | Type | Description |
|-------|------|-------------|
| `lpa` | string | Local Planning Authority name |
| `applications` | array[[PlanningApplication](#planningapplication)] | List of planning applications |
| `total_count` | integer | Total number of applications |

### PlanningApplication

Model for a single planning application.

| Field | Type | Description |
|-------|------|-------------|
| `reference` | string | Planning application reference number |
| `address` | string | Site address for the application |
| `proposal` | string | Description of the proposed development |
| `status` | string | Current status (Pending, Approved, Refused, etc.) |
| `received_date` | string | Date application was received (YYYY-MM-DD) |
| `decision_date` | string \| null | Date of decision if available |
| `decision` | string \| null | Decision outcome if available |
| `applicant_name` | string \| null | Name of the applicant |
| `application_type` | string \| null | Type of application (Full, Householder, Outline) |

### AirQualityResponse

Response model for air quality data.

| Field | Type | Description |
|-------|------|-------------|
| `area` | string | Geographic area name |
| `max_daqi` | integer (1-10) | Maximum Daily Air Quality Index |
| `summary` | string | Summary band (Low, Moderate, High, Very High) |
| `pollutants` | array[[Pollutant](#pollutant)] | List of pollutant measurements |
| `forecast_date` | string \| null | Date of the forecast (YYYY-MM-DD) |

### Pollutant

Model for a single pollutant measurement.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Pollutant name (NO2, PM2.5, O3, PM10, SO2, CO) |
| `value` | number | Measured value |
| `units` | string | Units of measurement (typically µg/m³) |
| `band` | string \| null | Air quality band (Low, Moderate, High, Very High) |
| `index` | integer \| null | DAQI index for this pollutant (1-10) |

### ErrorResponse

Standard error response model.

| Field | Type | Description |
|-------|------|-------------|
| `detail` | string | Human-readable error message |
| `code` | string \| null | Optional error code |

---

## Rate Limiting

Currently, the API does not implement rate limiting. For production deployments, consider implementing:

- **Per-IP rate limiting:** 100 requests/minute
- **Per-endpoint rate limiting:** 60 requests/minute for external API-dependent endpoints

---

## OpenAPI Specification

The API provides auto-generated OpenAPI documentation:

| Documentation | URL |
|---------------|-----|
| **Swagger UI** | `http://localhost:8000/docs` |
| **ReDoc** | `http://localhost:8000/redoc` |
| **OpenAPI JSON** | `http://localhost:8000/openapi.json` |

### OpenAPI Schema (JSON)

The complete OpenAPI specification is available at `/openapi.json`. This can be used to:

- Generate client SDKs
- Import into Postman/Insomnia
- Create API documentation portals

---

## Caching Behavior

All data endpoints implement caching to reduce external API calls:

| Endpoint | Cache TTL | Rationale |
|----------|-----------|-----------|
| `/api/bins` | 1 hour | Bin schedules rarely change during the day |
| `/api/planning` | 30 minutes | Application status can update during the day |
| `/api/air-quality` | 10 minutes | Air quality data is time-sensitive |

### Cache Behavior Notes

1. **First request:** Fetches from external API, caches result
2. **Subsequent requests:** Returns cached data if within TTL
3. **After TTL expires:** Next request fetches fresh data
4. **Cache is per-parameter:** Different parameters = different cache keys

**Example Cache Keys:**

```
bins:postcode=YO1 1AA
bins:uprn=100070123456
planning:lpa=City of York Council
planning:lpa=City of York Council:date_from=2025-01-01
air_quality:area=Greater London
```

---

## Development Mode (Mock Data)

When `MOCK_MODE=true` is set in the backend configuration:

- External APIs are not called
- Mock data is returned for all endpoints
- Useful for development without internet connectivity

### Available Mock Data

**Bin Collections:**
- `YO1 1AA` – City of York Council
- `SW1A 1AA` – Westminster City Council
- `M1 1AA` – Manchester City Council

**Planning Applications:**
- City of York Council
- Westminster City Council
- Manchester City Council

**Air Quality:**
- Yorkshire & Humber
- Greater London
- Greater Manchester
- West Midlands

---

## Related Documentation

- [README.md](./README.md) – Project overview and quick start
- [ARCHITECTURE.md](./ARCHITECTURE.md) – System architecture details
- [SYSTEM_FLOW.md](./SYSTEM_FLOW.md) – Sequence diagrams and data flows
