# System Architecture Diagram

This document contains the architecture diagram for the Local Council Data Explorer in Mermaid format.

## System Overview

```mermaid
graph TB
    subgraph Client["🖥️ Client Tier"]
        Browser["Web Browser"]
        
        subgraph React["React Application"]
            Layout["Layout Component"]
            BinPanel["BinPanel"]
            PlanningPanel["PlanningPanel"]
            AirPanel["AirQualityPanel"]
            useApi["useApi Hook"]
        end
    end

    subgraph Server["⚙️ Server Tier"]
        subgraph FastAPI["FastAPI Application"]
            CORS["CORS Middleware"]
            BinsRouter["/api/bins"]
            PlanningRouter["/api/planning"]
            AirRouter["/api/air-quality"]
            
            subgraph Services["Services Layer"]
                BinsService["BinsService"]
                PlanningService["PlanningService"]
                AirService["AirQualityService"]
            end
            
            Cache["InMemoryCache<br/>TTL-based"]
            
            subgraph Models["Pydantic Models"]
                BinModels["BinCollection<br/>BinCollectionResponse"]
                PlanningModels["PlanningApplication<br/>PlanningResponse"]
                AirModels["Pollutant<br/>AirQualityResponse"]
            end
        end
    end

    subgraph External["🌐 External APIs"]
        YorkAPI["City of York<br/>Waste API"]
        PlanningAPI["planning.data<br/>.gov.uk"]
        UKAIR["UK-AIR<br/>Defra API"]
    end

    Browser --> Layout
    Layout --> BinPanel
    Layout --> PlanningPanel
    Layout --> AirPanel
    BinPanel --> useApi
    PlanningPanel --> useApi
    AirPanel --> useApi

    useApi -->|HTTP/REST| CORS
    CORS --> BinsRouter
    CORS --> PlanningRouter
    CORS --> AirRouter

    BinsRouter --> BinsService
    PlanningRouter --> PlanningService
    AirRouter --> AirService

    BinsService --> Cache
    PlanningService --> Cache
    AirService --> Cache

    BinsService --> BinModels
    PlanningService --> PlanningModels
    AirService --> AirModels

    BinsService -->|httpx| YorkAPI
    PlanningService -->|httpx| PlanningAPI
    AirService -->|httpx| UKAIR
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant C as Cache
    participant E as External API

    U->>F: Load Page
    F->>B: GET /api/bins?postcode=YO1+1AA
    B->>C: Check Cache
    
    alt Cache Hit
        C-->>B: Return Cached Data
    else Cache Miss
        B->>E: Fetch External Data
        E-->>B: Raw JSON
        B->>B: Transform Data
        B->>C: Store with TTL
    end
    
    B-->>F: JSON Response
    F->>U: Render UI
```

## Component Architecture

```mermaid
graph LR
    subgraph Frontend["Frontend Components"]
        App["App.tsx<br/>(State Management)"]
        Layout["Layout.tsx<br/>(Navigation)"]
        
        subgraph Features["Feature Modules"]
            Bins["bins/<br/>BinPanel.tsx<br/>api.ts<br/>types.ts"]
            Planning["planning/<br/>PlanningPanel.tsx<br/>api.ts<br/>types.ts"]
            Air["air/<br/>AirQualityPanel.tsx<br/>api.ts<br/>types.ts"]
        end
        
        subgraph Hooks["Custom Hooks"]
            useApi["useApi.ts<br/>Loading/Error/Retry"]
        end
    end

    App --> Layout
    Layout --> Bins
    Layout --> Planning
    Layout --> Air
    Bins --> useApi
    Planning --> useApi
    Air --> useApi
```

## Cache Strategy

```mermaid
graph TB
    subgraph CacheFlow["Cache Flow"]
        Request["API Request"]
        GenKey["Generate Cache Key<br/>e.g., bins:postcode=YO1 1AA"]
        CheckCache["Check Cache"]
        
        subgraph Hit["Cache Hit Path"]
            ReturnCached["Return Cached Data"]
        end
        
        subgraph Miss["Cache Miss Path"]
            FetchAPI["Fetch from External API"]
            Transform["Transform Data"]
            StoreCache["Store with TTL<br/>Bins: 1hr<br/>Planning: 30min<br/>Air: 10min"]
        end
        
        Response["Return Response"]
    end

    Request --> GenKey
    GenKey --> CheckCache
    CheckCache -->|Hit| ReturnCached
    CheckCache -->|Miss| FetchAPI
    FetchAPI --> Transform
    Transform --> StoreCache
    ReturnCached --> Response
    StoreCache --> Response
```

## Error Handling Flow

```mermaid
graph TB
    subgraph ErrorFlow["Error Handling"]
        ExternalError["External API Error"]
        
        subgraph ServiceLayer["Service Layer"]
            Catch["Catch Exception"]
            Log["Log Error"]
            Fallback["Return Fallback<br/>or Re-raise"]
        end
        
        subgraph RouterLayer["Router Layer"]
            MapError["Map to HTTPException"]
            
            subgraph ErrorTypes["Error Type Mapping"]
                Timeout["TimeoutException → 503"]
                NotFound["HTTPStatusError 404 → 404"]
                ServerError["HTTPStatusError 5xx → 503"]
                Validation["ValueError → 400"]
                Unknown["Exception → 500"]
            end
        end
        
        subgraph Frontend["Frontend"]
            DisplayError["Display Error Message"]
            RetryButton["Show Retry Button"]
        end
    end

    ExternalError --> Catch
    Catch --> Log
    Log --> Fallback
    Fallback -->|Re-raise| MapError
    MapError --> Timeout
    MapError --> NotFound
    MapError --> ServerError
    MapError --> Validation
    MapError --> Unknown
    Timeout --> DisplayError
    NotFound --> DisplayError
    ServerError --> DisplayError
    Validation --> DisplayError
    Unknown --> DisplayError
    DisplayError --> RetryButton
```

## Deployment Architecture

```mermaid
graph TB
    subgraph Production["Production Deployment"]
        subgraph Docker["Docker Compose"]
            Frontend["Frontend Container<br/>nginx:alpine<br/>Port 3000"]
            Backend["Backend Container<br/>python:3.11-slim<br/>Port 8000"]
        end
        
        subgraph Network["Docker Network"]
            Bridge["council-network<br/>(bridge)"]
        end
    end

    subgraph External["External Services"]
        Internet["Internet"]
    end

    User["User"] --> Frontend
    Frontend -->|/api/*| Backend
    Backend --> Internet
```

---

## How to Render

These diagrams can be rendered in several ways:

1. **GitHub**: GitHub automatically renders Mermaid diagrams in markdown files
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Mermaid Live Editor**: https://mermaid.live
4. **Export as SVG/PNG**: Use Mermaid CLI (`npx @mermaid-js/mermaid-cli`)

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🖥️ | Client-side component |
| ⚙️ | Server-side component |
| 🌐 | External API |
| → | Data flow |
| ⟷ | Bidirectional communication |
