# Architecture

This document describes the system architecture and design decisions for the Local Council Data Explorer.

## Overview

The Local Council Data Explorer is a full-stack application for visualizing local council data including bin collections, planning applications, and air quality information.

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Vite
- **Data Sources**: Bin Collections, Planning Applications, Air Quality APIs

## Project Structure

### Backend (`/backend`)

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Application configuration settings
├── routers/                # API route handlers
│   ├── bins.py             # Bin collection endpoints
│   ├── planning.py         # Planning application endpoints
│   └── air_quality.py      # Air quality endpoints
├── services/               # Business logic layer
│   ├── bins_service.py     # Bin collection data processing
│   ├── planning_service.py # Planning application processing
│   └── air_service.py      # Air quality data processing
└── models/                 # Data models (Pydantic schemas)
    ├── bins.py             # Bin collection models
    ├── planning.py         # Planning application models
    └── air_quality.py      # Air quality models
```

### Frontend (`/frontend`)

```
frontend/src/
├── App.tsx                 # Root application component
├── main.tsx                # Application entry point
├── features/               # Feature-based modules
│   ├── bins/               # Bin collections feature
│   │   ├── BinPanel.tsx    # Bin display component
│   │   ├── api.ts          # Bin API functions
│   │   └── types.ts        # Bin TypeScript types
│   ├── planning/           # Planning applications feature
│   │   ├── PlanningPanel.tsx
│   │   ├── api.ts
│   │   └── types.ts
│   └── air/                # Air quality feature
│       ├── AirQualityPanel.tsx
│       ├── api.ts
│       └── types.ts
└── components/             # Shared UI components
    ├── Card.tsx            # Reusable card container
    ├── Layout.tsx          # Page layout wrapper
    └── ChartWrapper.tsx    # Chart display wrapper
```

## Architecture Principles

### Separation of Concerns

The codebase follows a clear separation of concerns:

1. **Routers** - Handle HTTP requests and route to appropriate services
2. **Services** - Contain business logic and data processing
3. **Models** - Define data structures for validation and serialization

### Feature-Based Frontend Architecture

The frontend uses a feature-based architecture where each domain (bins, planning, air quality) has its own:

- **Panel Component** - UI for displaying feature data
- **API Module** - Functions for backend communication
- **Types** - TypeScript interfaces for type safety

### Shared Components

Common UI components are placed in the `components/` directory to promote reuse:

- `Card` - Generic container component
- `Layout` - Consistent page structure
- `ChartWrapper` - Standard chart presentation

## API Design

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bins` | GET | Get bin collection schedules |
| `/api/planning` | GET | Get planning applications |
| `/api/air-quality` | GET | Get air quality data |
| `/health` | GET | Health check endpoint |

### Query Parameters

- **Bins**: `postcode`, `uprn`
- **Planning**: `lpa`, `date_from`, `date_to`
- **Air Quality**: `area`

## Design Decisions

### Why FastAPI?

- Modern, fast Python web framework
- Automatic OpenAPI documentation
- Built-in data validation with Pydantic
- Async support for efficient I/O operations

### Why React + TypeScript?

- Component-based architecture for reusability
- TypeScript provides type safety and better developer experience
- Vite for fast development and optimized builds

### Why Feature-Based Organization?

- Each feature is self-contained
- Easy to add new features without modifying existing code
- Clear ownership and maintainability

## Future Considerations

- Database integration for caching external API responses
- User authentication for personalized data
- Real-time updates using WebSockets
- Containerization with Docker for deployment
