# Local Council Data Explorer

**A full-stack application for visualizing UK local council data, including bin collection schedules, planning applications, and real-time air quality information.**

<!-- Quality Badges -->
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![Node.js 20+](https://img.shields.io/badge/Node.js-20+-339933.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](./docker-compose.yml)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/badge/linting-ruff-261230.svg)](https://docs.astral.sh/ruff/)

<!-- Technology Badges -->
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

---

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| **Frontend** | `https://local-council-explorer.vercel.app` |
| **Backend API** | `https://local-council-api.onrender.com` |
| **API Docs** | `https://local-council-api.onrender.com/docs` |

> **Note:** Live demo links are placeholders. Replace with actual deployment URLs after deployment.

---

## 📋 Project Summary

The Local Council Data Explorer aggregates and visualizes essential local council data for UK residents. By consolidating multiple council data sources into a single, intuitive interface, users can:

- **Check bin collection schedules** – Never miss a collection again with at-a-glance collection dates
- **Browse planning applications** – Stay informed about local development proposals and decisions
- **Monitor air quality** – Real-time DAQI (Daily Air Quality Index) readings with pollutant breakdowns

This project demonstrates modern full-stack development practices including API aggregation, data transformation, caching strategies, and responsive UI design.

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async Python web framework |
| **Pydantic** | Data validation and serialization |
| **httpx** | Async HTTP client for external API calls |
| **pydantic-settings** | Configuration management with .env support |
| **uvicorn** | ASGI server for production deployment |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | Component-based UI library |
| **TypeScript** | Type-safe JavaScript superset |
| **Vite** | Fast build tool and dev server |
| **Recharts** | Declarative charting library |

### External APIs
| API | Data Source |
|-----|-------------|
| **City of York Waste API** | Bin collection schedules |
| **planning.data.gov.uk** | Planning application data |
| **UK-AIR Defra API** | Air quality measurements and forecasts |

---

## ✨ Features

### 🗑️ Bin Collections
- Look up collection schedules by postcode or UPRN
- Visual countdown chart showing days until next collection
- Automatic bin type recognition (Refuse, Recycling, Garden Waste)
- Today/Tomorrow badges for imminent collections

### 🏗️ Planning Applications
- Search planning applications by Local Planning Authority
- Filter by date range
- View application status, decisions, and key dates
- Support for multiple application types (Full, Householder, Outline)

### 🌬️ Air Quality
- Real-time DAQI readings with severity bands (Low/Moderate/High/Very High)
- Pollutant breakdown (NO₂, PM2.5, PM10, O₃, SO₂)
- Regional air quality forecasts
- Color-coded visual indicators

### 🔧 Technical Features
- **In-memory caching** with configurable TTLs per endpoint
- **Mock mode** for offline development without external API dependencies
- **Automatic retry logic** with exponential backoff
- **Comprehensive error handling** with informative user feedback
- **Responsive design** optimized for desktop and mobile

---

## 📁 Project Structure

```
local-council-data-explorer/
├── backend/                        # FastAPI backend application
│   ├── main.py                     # Application entry point
│   ├── config.py                   # Configuration management
│   ├── routers/                    # HTTP route handlers
│   │   ├── bins.py                 # /api/bins endpoint
│   │   ├── planning.py             # /api/planning endpoint
│   │   └── air_quality.py          # /api/air-quality endpoint
│   ├── services/                   # Business logic layer
│   │   ├── bins_service.py         # Bin collection data processing
│   │   ├── planning_service.py     # Planning data processing
│   │   ├── air_service.py          # Air quality data processing
│   │   └── cache.py                # In-memory caching
│   ├── models/                     # Pydantic data models
│   │   ├── bins.py                 # Bin collection schemas
│   │   ├── planning.py             # Planning schemas
│   │   ├── air_quality.py          # Air quality schemas
│   │   └── errors.py               # Error response schemas
│   ├── tests/                      # Pytest test suite
│   ├── Dockerfile                  # Backend container
│   └── requirements.txt            # Python dependencies
├── frontend/                       # React frontend application
│   ├── src/
│   │   ├── main.tsx                # Application bootstrap
│   │   ├── App.tsx                 # Root component
│   │   ├── api/                    # API client configuration
│   │   │   └── client.ts           # Centralized API config
│   │   ├── components/             # Shared UI components
│   │   │   ├── Layout.tsx          # Page layout with navigation
│   │   │   ├── Card.tsx            # Container component
│   │   │   └── ChartWrapper.tsx    # Chart display wrapper
│   │   ├── features/               # Feature modules
│   │   │   ├── bins/               # Bin collections feature
│   │   │   ├── planning/           # Planning applications feature
│   │   │   └── air/                # Air quality feature
│   │   └── hooks/                  # Custom React hooks
│   │       └── useApi.ts           # Async data fetching hook
│   ├── Dockerfile                  # Frontend container
│   ├── nginx.conf                  # Production nginx config
│   └── package.json                # Node dependencies
├── docs/                           # Documentation assets
│   └── SCREENSHOTS.md              # Screenshot capture guide
├── portfolio/                      # Portfolio documentation
│   ├── README.md                   # Portfolio overview
│   ├── CASE_STUDY.md               # Detailed case study
│   └── ARCHITECTURE_DIAGRAMS.md    # Mermaid diagrams
├── docker-compose.yml              # Container orchestration
├── README.md                       # Main project documentation
├── Architecture.md                 # System architecture
├── API_REFERENCE.md                # API endpoint reference
├── SYSTEM_FLOW.md                  # Sequence diagrams
├── SETUP.md                        # Installation guide
└── PORTFOLIO_NOTES.md              # Interview talking points
```

---

## 🏗️ Architecture Overview

The application follows a clean separation of concerns with a layered architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  BinPanel   │  │PlanningPanel│  │   AirQualityPanel       │  │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘  │
│         │                │                      │               │
│  ┌──────▼────────────────▼──────────────────────▼────────────┐  │
│  │                    Feature APIs                           │  │
│  │           (fetchBinCollections, fetchPlanning, etc.)       │  │
│  └────────────────────────────┬─────────────────────────────┘  │
└───────────────────────────────┼─────────────────────────────────┘
                                │ HTTP/REST
┌───────────────────────────────▼─────────────────────────────────┐
│                       Backend (FastAPI)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ bins router │  │  planning   │  │   air_quality router    │  │
│  │   /api/bins │  │   router    │  │   /api/air-quality      │  │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘  │
│         │                │                      │               │
│  ┌──────▼────────────────▼──────────────────────▼────────────┐  │
│  │                     Services Layer                        │  │
│  │     (BinsService, PlanningService, AirQualityService)     │  │
│  └──────┬────────────────┬──────────────────────┬────────────┘  │
│         │                │                      │               │
│  ┌──────▼────────────────▼──────────────────────▼────────────┐  │
│  │                    In-Memory Cache                         │  │
│  │            (TTL-based caching per data type)              │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
    ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
    │  York Waste   │   │ planning.data │   │   UK-AIR      │
    │     API       │   │   .gov.uk     │   │   Defra       │
    └───────────────┘   └───────────────┘   └───────────────┘
```

For detailed architecture documentation, see [Architecture.md](./Architecture.md).

---

## 📸 Screenshots

> **Note:** Screenshots will be added after initial deployment. See [docs/SCREENSHOTS.md](./docs/SCREENSHOTS.md) for capture instructions.

| Bin Collections | Planning Applications | Air Quality |
|-----------------|----------------------|-------------|
| ![Bins Screenshot](./docs/screenshots/bins.png) | ![Planning Screenshot](./docs/screenshots/planning.png) | ![Air Quality Screenshot](./docs/screenshots/air-quality.png) |

---

## 🚀 Local Development

### Prerequisites

- **Python 3.11+** – Backend runtime
- **Node.js 20+** – Frontend build tooling
- **npm** or **pnpm** – Package manager

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn httpx pydantic pydantic-settings

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`.

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173` with hot module replacement (HMR).

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Application settings
DEBUG=true
MOCK_MODE=true  # Set to false to use real external APIs

# External API settings (optional - only needed when MOCK_MODE=false)
BINS_API_KEY=your_api_key_here
PLANNING_API_KEY=your_api_key_here
AIR_QUALITY_API_KEY=your_api_key_here

# Cache settings (in seconds)
CACHE_TTL_BINS=3600
CACHE_TTL_PLANNING=1800
CACHE_TTL_AIR_QUALITY=600
```

### Running Tests

```bash
# Backend tests
cd backend
pip install pytest pytest-asyncio
pytest

# Frontend linting
cd frontend
npm run lint
```

---

## 🌍 Deployment

### Backend Deployment (Render)

1. **Create a Render account** at [render.com](https://render.com)

2. **Create a new Web Service:**
   - Connect your GitHub repository
   - Select the `backend` directory as the root
   - Set runtime to Python 3
   
3. **Configure build settings:**
   ```yaml
   Build Command: pip install fastapi uvicorn httpx pydantic pydantic-settings
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Set environment variables:**
   - `MOCK_MODE=false` (for production)
   - Add API keys as needed

5. **Deploy** – Render will automatically build and deploy your service

### Frontend Deployment (Vercel)

1. **Create a Vercel account** at [vercel.com](https://vercel.com)

2. **Import your GitHub repository:**
   - Select the `frontend` directory as the root
   - Framework preset: Vite

3. **Configure environment variables:**
   ```
   VITE_API_BASE_URL=https://your-render-backend-url.onrender.com
   ```

4. **Update `vite.config.ts`** for production API proxy:
   ```typescript
   export default defineConfig({
     plugins: [react()],
     define: {
       'import.meta.env.VITE_API_BASE_URL': JSON.stringify(process.env.VITE_API_BASE_URL)
     }
   })
   ```

5. **Deploy** – Vercel will automatically build and deploy on every push

### Alternative Deployment Options

| Platform | Backend | Frontend |
|----------|---------|----------|
| Docker | ✅ Containerize with `Dockerfile` | ✅ Multi-stage build |
| Railway | ✅ Python buildpack | ✅ Node.js buildpack |
| Fly.io | ✅ Python/uvicorn | ✅ Static site hosting |
| AWS | Lambda + API Gateway | S3 + CloudFront |

---

## 📖 Documentation

### Technical Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE_OVERVIEW.md](./docs/ARCHITECTURE_OVERVIEW.md) | System architecture and design patterns |
| [docs/BACKEND_STRUCTURE.md](./docs/BACKEND_STRUCTURE.md) | Backend module organization and patterns |
| [docs/FRONTEND_STRUCTURE.md](./docs/FRONTEND_STRUCTURE.md) | Frontend component architecture |
| [docs/DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md) | Production deployment instructions |
| [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [docs/CONTRIBUTING_GUIDE.md](./docs/CONTRIBUTING_GUIDE.md) | Contribution guidelines |

### Reference Documentation

| Document | Description |
|----------|-------------|
| [Architecture.md](./Architecture.md) | Detailed system architecture |
| [SYSTEM_FLOW.md](./SYSTEM_FLOW.md) | Sequence diagrams and data flow |
| [API_REFERENCE.md](./API_REFERENCE.md) | Complete API endpoint reference |
| [SETUP.md](./SETUP.md) | Installation and setup guide |
| [PORTFOLIO_NOTES.md](./PORTFOLIO_NOTES.md) | Interview talking points |
| [docs/SYSTEM_VERIFICATION_OPTION_A.md](./docs/SYSTEM_VERIFICATION_OPTION_A.md) | System integrity verification |

### Portfolio Resources

| Document | Description |
|----------|-------------|
| [portfolio/README.md](./portfolio/README.md) | Portfolio overview |
| [portfolio/CASE_STUDY.md](./portfolio/CASE_STUDY.md) | Detailed case study |
| [portfolio/ARCHITECTURE_DIAGRAMS.md](./portfolio/ARCHITECTURE_DIAGRAMS.md) | Mermaid diagrams |

---

## 💼 What This Project Demonstrates

This project showcases professional-grade full-stack development skills:

### Backend Engineering
- **API Design** – RESTful API design with FastAPI, including automatic OpenAPI documentation
- **External API Integration** – Aggregating data from multiple third-party APIs with error handling
- **Caching Strategies** – In-memory TTL-based caching to reduce API load and improve response times
- **Clean Architecture** – Separation of concerns with routers, services, and models layers
- **Error Handling** – Comprehensive error handling with informative responses

### Frontend Development
- **Modern React** – React 19 with hooks, functional components, and TypeScript
- **State Management** – Custom hooks for async data fetching with loading/error states
- **Data Visualization** – Interactive charts with Recharts
- **Feature-Based Architecture** – Modular feature organization for maintainability
- **Type Safety** – Full TypeScript coverage for compile-time error detection

### DevOps & Infrastructure
- **Environment Configuration** – Pydantic-settings for type-safe configuration management
- **Development Tooling** – Vite for fast development iteration
- **API Proxy** – Development proxy configuration for seamless frontend-backend integration

### Software Engineering Practices
- **Mock Mode** – Development without external API dependencies
- **Defensive Programming** – Fallback responses for graceful degradation
- **Code Organization** – Clear, consistent project structure
- **Documentation** – Comprehensive inline documentation and API docs

---

## 🔮 Future Improvements

### Short-Term Enhancements
- [ ] Additional council integrations (beyond City of York)
- [ ] CI/CD pipeline with GitHub Actions
- [ ] End-to-end testing with Playwright

### Medium-Term Enhancements
- [ ] User accounts for saved postcodes/preferences
- [ ] Email/SMS notifications for bin collections
- [ ] WebSocket support for live air quality updates
- [ ] Database persistence (PostgreSQL/SQLite)

### Long-Term Vision
- [ ] Mobile application (React Native)
- [ ] Historical trend analysis and insights
- [ ] Machine learning for bin collection disruption prediction
- [ ] Multi-region deployment for redundancy

---

## 👤 Author

**Local Council Data Explorer**

This project was built as a portfolio demonstration piece showcasing production-grade full-stack development skills.

- 📧 Contact via GitHub Issues
- 🔗 See [PORTFOLIO_NOTES.md](./PORTFOLIO_NOTES.md) for interview talking points

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<p align="center">
  Built with ❤️ for UK local councils and their residents
</p>
