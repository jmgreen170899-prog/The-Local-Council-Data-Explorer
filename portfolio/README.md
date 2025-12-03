# Portfolio Overview

## Local Council Data Explorer

A production-ready full-stack web application for aggregating and visualizing UK local council data.

---

## 🎯 Project Purpose

Consolidate multiple UK council data sources (bin collections, planning applications, air quality) into a single, intuitive interface that demonstrates modern full-stack engineering practices.

---

## ✨ Feature List

| Feature | Description |
|---------|-------------|
| **Bin Collections** | Look up collection schedules by postcode with visual countdown |
| **Planning Applications** | Search and filter local development proposals |
| **Air Quality** | Real-time DAQI readings with pollutant breakdowns |
| **Intelligent Caching** | TTL-based caching to reduce API load |
| **Mock Mode** | Offline development without external dependencies |
| **Responsive Design** | Mobile and desktop optimized |
| **Error Handling** | Automatic retries with exponential backoff |

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** - Runtime
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and serialization
- **httpx** - Async HTTP client
- **uvicorn** - ASGI server

### Frontend
- **React 19** - Component-based UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Recharts** - Declarative charting

### DevOps
- **Docker** - Containerization
- **nginx** - Production web server
- **docker-compose** - Multi-container orchestration

---

## 📁 Project Structure

```
local-council-data-explorer/
├── backend/                    # FastAPI backend
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   ├── routers/                # HTTP route handlers
│   ├── services/               # Business logic layer
│   ├── models/                 # Pydantic models
│   ├── tests/                  # Pytest test suite
│   ├── Dockerfile              # Backend container
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # Shared UI components
│   │   ├── features/           # Feature modules
│   │   └── hooks/              # Custom React hooks
│   ├── Dockerfile              # Frontend container
│   └── package.json            # Node dependencies
├── portfolio/                  # Portfolio documentation
│   ├── README.md               # This file
│   ├── CASE_STUDY.md           # Detailed project analysis
│   └── ARCHITECTURE_DIAGRAMS.md # Mermaid diagrams
├── docker-compose.yml          # Container orchestration
└── README.md                   # Main project documentation
```

---

## 🔑 Key Engineering Highlights

### 1. Clean Architecture
- Layered backend with routers, services, and models
- Feature-based frontend organization
- Clear separation of concerns

### 2. API Aggregation
- Integrates 3 external government APIs
- Normalizes disparate data formats
- Handles API inconsistencies gracefully

### 3. Caching Strategy
- Thread-safe in-memory cache
- Configurable TTL per data type
- Lazy expiration on access

### 4. Error Handling
- Comprehensive exception mapping
- Automatic retry with backoff
- Graceful degradation with fallbacks

### 5. Type Safety
- Full TypeScript coverage (frontend)
- Pydantic models (backend)
- Auto-generated OpenAPI docs

---

## 📊 Metrics

| Metric | Value |
|--------|-------|
| Backend Tests | 66 passing |
| Frontend Linting | ✅ Clean |
| Code Coverage | ~60% |
| Build Time | <1 second (Vite) |
| Container Size | ~150MB (backend) |

---

## 🚀 Quick Start

### Local Development

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Main project documentation |
| [CASE_STUDY.md](./CASE_STUDY.md) | Detailed portfolio case study |
| [ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md) | System architecture diagrams |
| [API_REFERENCE.md](../API_REFERENCE.md) | Complete API documentation |
| [Architecture.md](../Architecture.md) | Technical architecture details |
| [SYSTEM_FLOW.md](../SYSTEM_FLOW.md) | Sequence diagrams and flows |

---

## 🎓 Skills Demonstrated

| Category | Skills |
|----------|--------|
| **Backend** | Python, FastAPI, async programming, API design |
| **Frontend** | React, TypeScript, state management, data visualization |
| **Data** | ETL patterns, data transformation, caching |
| **DevOps** | Docker, nginx, container orchestration |
| **Testing** | pytest, unit testing, integration testing |
| **Documentation** | OpenAPI, markdown, architecture diagrams |

---

## 📫 Contact

For questions about this project, please open an issue on GitHub.

---

*Built with ❤️ as a portfolio demonstration piece*
