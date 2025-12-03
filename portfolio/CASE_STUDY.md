# Local Council Data Explorer

## Portfolio Case Study

### Project Overview

The **Local Council Data Explorer** is a full-stack web application that aggregates and visualizes UK local council data from multiple government APIs. Built as a portfolio demonstration piece, it showcases modern software engineering practices including API aggregation, data transformation, caching strategies, and responsive UI design.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Architecture](#solution-architecture)
- [Technical Implementation](#technical-implementation)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Challenges & Solutions](#challenges--solutions)
- [Future Enhancements](#future-enhancements)
- [Demo Script](#demo-script)

---

## Problem Statement

UK residents often need to access multiple council services that are scattered across different websites:

1. **Bin Collection Schedules** - When is my next bin collection?
2. **Planning Applications** - What developments are proposed in my area?
3. **Air Quality Data** - Is it safe to exercise outdoors today?

Each of these requires navigating different interfaces, often with poor mobile experiences and no unified view.

### Target Users

- **Homeowners** wanting quick access to bin collection dates
- **Community groups** monitoring local planning decisions
- **Health-conscious individuals** checking air quality before outdoor activities
- **Developers** learning about API aggregation patterns

---

## Solution Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │  BinPanel    │ │PlanningPanel │ │   AirQualityPanel        │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     Services Layer                        │   │
│  │    Data Transformation • Caching • Error Handling         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌───────────┐      ┌───────────┐      ┌───────────┐
    │City of    │      │planning.  │      │ UK-AIR    │
    │York API   │      │data.gov.uk│      │ Defra     │
    └───────────┘      └───────────┘      └───────────┘
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI** | Async support for non-blocking I/O, automatic OpenAPI docs |
| **In-memory caching** | Simple, fast, no external dependencies (Redis, etc.) |
| **Feature-based frontend structure** | Scalable, each feature is self-contained |
| **Mock mode** | Development without internet/API dependencies |
| **TypeScript** | Type safety across the full stack |

---

## Technical Implementation

### Backend Architecture

The backend follows a layered architecture:

```
backend/
├── main.py              # FastAPI app entry, CORS, lifespan
├── config.py            # Pydantic settings management
├── routers/             # HTTP route handlers
│   ├── bins.py          # /api/bins endpoints
│   ├── planning.py      # /api/planning endpoints
│   └── air_quality.py   # /api/air-quality endpoints
├── services/            # Business logic layer
│   ├── bins_service.py  # External API integration
│   ├── planning_service.py
│   ├── air_service.py
│   └── cache.py         # Thread-safe in-memory cache
├── models/              # Pydantic data models
│   ├── bins.py
│   ├── planning.py
│   └── air_quality.py
└── tests/               # Pytest test suite
```

### Caching Strategy

Each data type has its own cache with appropriate TTL:

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Bin Collections | 1 hour | Schedules rarely change |
| Planning | 30 min | Status can update during day |
| Air Quality | 10 min | Time-sensitive readings |

### Data Transformation Pipeline

External API responses are transformed through a consistent pipeline:

```
External API → Service Transform → Pydantic Model → JSON Response
```

Example transformation (City of York API):
- `"GREY BIN"` → `"Refuse"`
- `"2025-12-09T00:00:00"` → `"2025-12-09"`
- Sort by collection date

### Frontend Architecture

The frontend uses a feature-based structure:

```
frontend/src/
├── App.tsx              # Main component with tab navigation
├── components/          # Shared UI components
│   ├── Layout.tsx       # Navigation wrapper
│   ├── Card.tsx         # Container component
│   └── ChartWrapper.tsx # Responsive chart wrapper
├── features/            # Domain-specific modules
│   ├── bins/
│   │   ├── BinPanel.tsx # UI component
│   │   ├── api.ts       # API functions with retry
│   │   └── types.ts     # TypeScript interfaces
│   ├── planning/
│   └── air/
└── hooks/
    └── useApi.ts        # Generic async data hook
```

---

## Key Features

### 🗑️ Bin Collections

- Look up schedules by postcode or UPRN
- Visual countdown chart (days until collection)
- Automatic bin type recognition
- Today/Tomorrow badges

### 🏗️ Planning Applications

- Search by Local Planning Authority
- Filter by date range
- View application status and decisions
- Support for multiple application types

### 🌬️ Air Quality

- Real-time DAQI (1-10 scale)
- Pollutant breakdown (NO₂, PM2.5, PM10, O₃)
- Health advice based on readings
- Color-coded severity bands

### Technical Features

- **Intelligent caching** with per-endpoint TTLs
- **Mock mode** for offline development
- **Automatic retry** with exponential backoff
- **Comprehensive error handling**
- **Responsive design** for mobile/desktop

---

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Runtime |
| FastAPI | Web framework |
| Pydantic | Validation |
| httpx | Async HTTP client |
| uvicorn | ASGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 19 | UI library |
| TypeScript 5 | Type safety |
| Vite | Build tool |
| Recharts | Data visualization |

### DevOps
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| nginx | Production serving |
| GitHub Actions | CI/CD (planned) |

---

## Challenges & Solutions

### Challenge 1: Inconsistent External APIs

**Problem**: Each government API returns data in different formats.

**Solution**: Created service layer that normalizes all responses into consistent Pydantic models. Added extensive field mapping (e.g., `"GREY BIN"` → `"Refuse"`).

### Challenge 2: API Rate Limits & Availability

**Problem**: External APIs may be slow, rate-limited, or unavailable.

**Solution**: 
- Implemented TTL-based caching to reduce API calls
- Added retry logic with exponential backoff
- Created fallback responses for graceful degradation
- Mock mode for development

### Challenge 3: Type Safety Across Stack

**Problem**: Ensuring frontend/backend types stay synchronized.

**Solution**: TypeScript interfaces mirror Pydantic models. Both are documented in API_REFERENCE.md for manual verification.

---

## Future Enhancements

### Short-term
- [ ] Database persistence (SQLite/PostgreSQL)
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Additional council integrations

### Medium-term
- [ ] User accounts for saved postcodes
- [ ] Email/SMS alerts for bin collections
- [ ] WebSocket for live air quality updates

### Long-term
- [ ] Mobile app (React Native)
- [ ] Historical trend analysis
- [ ] ML-based prediction (bin disruptions)

---

## Demo Script

For a video walkthrough or live demo, follow this script:

### 1. Introduction (30 seconds)
- "This is the Local Council Data Explorer, a full-stack application for UK council data."
- Show the main dashboard

### 2. Bin Collections (1 minute)
- Click "Bin Collections" tab
- "Enter a postcode like YO1 1AA"
- Point out the chart showing days until collection
- Show Today/Tomorrow badges

### 3. Planning Applications (1 minute)
- Switch to "Planning" tab
- "Search for City of York Council"
- Show the application list
- Demonstrate date filtering

### 4. Air Quality (1 minute)
- Switch to "Air Quality" tab
- "Shows the current Daily Air Quality Index"
- Explain the pollutant breakdown
- Show the severity bands

### 5. Technical Highlights (1 minute)
- Show Swagger docs at /docs
- Demonstrate the health endpoint
- Mention caching, error handling, mock mode

### 6. Code Architecture (30 seconds)
- Brief tour of backend structure
- Show a service file (transformation logic)
- Show a frontend feature module

---

## Screenshots

> Note: Replace these placeholders with actual screenshots

| Feature | Screenshot |
|---------|------------|
| Dashboard | ![Dashboard](./screenshots/dashboard.png) |
| Bin Collections | ![Bins](./screenshots/bins.png) |
| Planning | ![Planning](./screenshots/planning.png) |
| Air Quality | ![Air Quality](./screenshots/air-quality.png) |
| API Docs | ![API Docs](./screenshots/api-docs.png) |

---

## Conclusion

The Local Council Data Explorer demonstrates:

1. **Full-stack proficiency** - Python backend, TypeScript frontend
2. **API design** - RESTful endpoints with OpenAPI documentation
3. **Data engineering** - ETL patterns, caching, transformation
4. **Clean architecture** - Layered services, feature-based frontend
5. **Production readiness** - Docker, error handling, logging

This project showcases the ability to build production-grade applications that aggregate external data sources into a unified, user-friendly interface.

---

*Built with ❤️ for UK local councils and their residents*
