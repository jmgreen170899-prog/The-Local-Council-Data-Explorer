# Setup Guide

This document provides comprehensive setup instructions for the Local Council Data Explorer project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Docker Setup](#docker-setup)
- [Mock Mode](#mock-mode)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Rebuilding the System](#rebuilding-the-system)

---

## Prerequisites

Before getting started, ensure you have the following installed:

| Requirement | Minimum Version | Purpose |
|-------------|-----------------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 20+ | Frontend build tooling |
| **npm** or **pnpm** | Latest | Package manager |
| **Docker** | 20+ | Container runtime (optional) |
| **Docker Compose** | v2+ | Container orchestration (optional) |

### Verify Prerequisites

```bash
# Check Python version
python --version
# Expected: Python 3.11.x or higher

# Check Node.js version
node --version
# Expected: v20.x.x or higher

# Check npm version
npm --version

# Check Docker (optional)
docker --version
docker compose version
```

---

## Local Development Setup

### Backend Setup

1. **Navigate to the backend directory:**

   ```bash
   cd backend
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**

   ```bash
   # On macOS/Linux:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment configuration (optional):**

   ```bash
   cp .env.example .env
   # Edit .env to configure settings
   ```

6. **Start the development server:**

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Verify the backend is running:**

   - Open `http://localhost:8000` – API root info
   - Open `http://localhost:8000/health` – Health check
   - Open `http://localhost:8000/docs` – Swagger UI documentation
   - Open `http://localhost:8000/redoc` – ReDoc documentation

### Frontend Setup

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm run dev
   ```

4. **Verify the frontend is running:**

   - Open `http://localhost:5173` – Main application

The Vite development server includes a proxy configuration that forwards `/api/*` requests to the backend at `http://localhost:8000`.

---

## Docker Setup

Docker provides the easiest way to run the complete stack.

### Quick Start

```bash
# From the project root directory
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

### Step-by-Step Docker Setup

1. **Build the containers:**

   ```bash
   docker compose build
   ```

2. **Start the services:**

   ```bash
   docker compose up -d
   ```

3. **Verify containers are running:**

   ```bash
   docker compose ps
   ```

   Expected output:
   ```
   NAME                      STATUS      PORTS
   council-explorer-api      healthy     0.0.0.0:8000->8000/tcp
   council-explorer-web      healthy     0.0.0.0:3000->80/tcp
   ```

4. **Access the application:**

   | Service | URL |
   |---------|-----|
   | Frontend | `http://localhost:3000` |
   | Backend API | `http://localhost:8000` |
   | API Docs (Swagger) | `http://localhost:8000/docs` |
   | API Docs (ReDoc) | `http://localhost:8000/redoc` |
   | Health Check | `http://localhost:8000/health` |

### Docker Commands Reference

```bash
# Start services in background
docker compose up -d

# Start services with log output
docker compose up

# Rebuild and start services
docker compose up --build

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# View running containers
docker compose ps

# View logs for all services
docker compose logs -f

# View logs for specific service
docker compose logs -f backend
docker compose logs -f frontend

# Execute command in container
docker compose exec backend bash
docker compose exec frontend sh

# Restart a specific service
docker compose restart backend
```

---

## Mock Mode

Mock mode allows development without external API dependencies. When enabled, the backend returns realistic sample data instead of calling external APIs.

### Enabling Mock Mode

**Option 1: Environment variable**

```bash
# In backend/.env
MOCK_MODE=true
```

**Option 2: Docker Compose (default)**

The `docker-compose.yml` enables mock mode by default:
```yaml
environment:
  - MOCK_MODE=true
```

### Mock Data Available

| Endpoint | Supported Values |
|----------|------------------|
| `/api/bins` | `YO1 1AA`, `SW1A 1AA`, `M1 1AA` |
| `/api/planning` | `City of York Council`, `Westminster City Council`, `Manchester City Council` |
| `/api/air-quality` | `Yorkshire & Humber`, `Greater London`, `Greater Manchester`, `West Midlands` |

### Disabling Mock Mode

To use real external APIs:

1. Set `MOCK_MODE=false` in your environment
2. Ensure network connectivity to external APIs:
   - City of York Waste API
   - planning.data.gov.uk
   - UK-AIR Defra API

---

## Environment Variables

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug logging |
| `MOCK_MODE` | `true` | Use mock data instead of external APIs |
| `API_VERSION` | `v1` | API version string |
| `BINS_API_BASE_URL` | `https://waste-api.york.gov.uk/api/Collections` | York Waste API URL |
| `PLANNING_API_BASE_URL` | `https://www.planning.data.gov.uk` | Planning API URL |
| `AIR_QUALITY_API_BASE_URL` | `https://api.erg.ic.ac.uk/AirQuality` | UK-AIR API URL |
| `CACHE_TTL_BINS` | `3600` | Bin data cache TTL (seconds) |
| `CACHE_TTL_PLANNING` | `1800` | Planning data cache TTL (seconds) |
| `CACHE_TTL_AIR_QUALITY` | `600` | Air quality data cache TTL (seconds) |
| `HTTP_TIMEOUT` | `30.0` | HTTP request timeout (seconds) |
| `HTTP_MAX_RETRIES` | `3` | Maximum retry attempts |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `""` (empty) | Backend API base URL |

For local development, leave `VITE_API_BASE_URL` empty – Vite's proxy handles API requests.

For Docker deployments, set to the backend container name:
```
VITE_API_BASE_URL=http://council-explorer-api:8000
```

---

## Troubleshooting

### Common Issues

#### Backend won't start

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

#### Frontend API calls fail

**Problem:** Network errors or CORS errors in browser console

**Solution:** Ensure backend is running on port 8000. The Vite proxy forwards `/api/*` requests to `http://localhost:8000`.

#### Docker container fails health check

**Problem:** Container shows as `unhealthy`

**Solution:** Check container logs:
```bash
docker compose logs backend
docker compose logs frontend
```

Common causes:
- Port already in use (try different ports)
- Missing environment variables
- Build errors in Dockerfile

#### Mock data not returning

**Problem:** API returns empty or error responses in mock mode

**Solution:** Verify `MOCK_MODE=true` is set:
```bash
# Check backend logs
docker compose logs backend | grep -i mock
```

### Port Conflicts

If default ports are in use, modify `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change 8000 to 8001
  frontend:
    ports:
      - "3001:80"    # Change 3000 to 3001
```

---

## Rebuilding the System

### Full Rebuild (Docker)

```bash
# Stop all containers
docker compose down

# Remove images
docker compose down --rmi all

# Rebuild and start
docker compose up --build -d
```

### Backend Rebuild

```bash
cd backend

# Clean up
rm -rf __pycache__ .pytest_cache

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run tests
pytest

# Start server
uvicorn main:app --reload
```

### Frontend Rebuild

```bash
cd frontend

# Clean up
rm -rf node_modules dist

# Reinstall dependencies
npm install

# Run linting
npm run lint

# Build production bundle
npm run build

# Start dev server
npm run dev
```

---

## Next Steps

After setup is complete:

1. **Explore the API documentation** at `http://localhost:8000/docs`
2. **Review the architecture** in [Architecture.md](./Architecture.md)
3. **Understand the data flows** in [SYSTEM_FLOW.md](./SYSTEM_FLOW.md)
4. **Check the API reference** in [API_REFERENCE.md](./API_REFERENCE.md)

---

*For additional help, please open an issue on GitHub.*
