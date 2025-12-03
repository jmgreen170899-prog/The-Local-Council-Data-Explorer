# Deployment Guide

> Step-by-step instructions for deploying the Local Council Data Explorer to production environments.

---

## Table of Contents

- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Backend Deployment (Render)](#backend-deployment-render)
- [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
- [Alternative Platforms](#alternative-platforms)
- [Environment Configuration](#environment-configuration)
- [Health Monitoring](#health-monitoring)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Troubleshooting Deployments](#troubleshooting-deployments)

---

## Deployment Options

| Strategy | Best For | Complexity |
|----------|----------|------------|
| **Docker Compose** | Self-hosted, VPS | Medium |
| **Render + Vercel** | Serverless, managed | Low |
| **Railway** | All-in-one platform | Low |
| **AWS/GCP/Azure** | Enterprise scale | High |
| **Kubernetes** | Microservices, scale | High |

---

## Docker Deployment

### Prerequisites

- Docker 20+ installed
- Docker Compose v2+ installed
- At least 1GB RAM available
- Ports 3000 and 8000 available

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/local-council-data-explorer.git
cd local-council-data-explorer

# Start all services
docker compose up -d

# Verify containers are running
docker compose ps
```

Expected output:

```
NAME                      STATUS      PORTS
council-explorer-api      healthy     0.0.0.0:8000->8000/tcp
council-explorer-web      running     0.0.0.0:3000->80/tcp
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

### Production Configuration

For production deployments, modify `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - DEBUG=false
      - MOCK_MODE=false  # Use real APIs
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  frontend:
    restart: always
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
```

### Docker Commands Reference

```bash
# Start in background
docker compose up -d

# Start with rebuild
docker compose up --build -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Full cleanup (including volumes)
docker compose down -v --rmi all

# Restart specific service
docker compose restart backend
```

---

## Backend Deployment (Render)

[Render](https://render.com) provides an easy way to deploy the FastAPI backend.

### Step 1: Create Render Account

1. Sign up at [render.com](https://render.com)
2. Connect your GitHub account

### Step 2: Create Web Service

1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure settings:

| Setting | Value |
|---------|-------|
| **Name** | `council-explorer-api` |
| **Root Directory** | `backend` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

### Step 3: Configure Environment Variables

Add the following environment variables in Render dashboard:

| Variable | Value |
|----------|-------|
| `MOCK_MODE` | `false` |
| `DEBUG` | `false` |
| `CACHE_TTL_BINS` | `3600` |
| `CACHE_TTL_PLANNING` | `1800` |
| `CACHE_TTL_AIR_QUALITY` | `600` |

### Step 4: Deploy

1. Click **Create Web Service**
2. Render will automatically build and deploy
3. Your API will be available at `https://council-explorer-api.onrender.com`

### Health Check Configuration

In Render dashboard, set:

- **Health Check Path**: `/health`
- **Health Check Period**: 30 seconds

---

## Frontend Deployment (Vercel)

[Vercel](https://vercel.com) is ideal for deploying the React frontend.

### Step 1: Create Vercel Account

1. Sign up at [vercel.com](https://vercel.com)
2. Connect your GitHub account

### Step 2: Import Project

1. Click **Add New** → **Project**
2. Import your GitHub repository
3. Configure settings:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### Step 3: Configure Environment Variables

Add environment variable:

| Variable | Value |
|----------|-------|
| `VITE_API_BASE_URL` | `https://council-explorer-api.onrender.com` |

### Step 4: Deploy

1. Click **Deploy**
2. Vercel will build and deploy automatically
3. Your frontend will be available at `https://council-explorer.vercel.app`

### Custom Domain

1. Go to **Settings** → **Domains**
2. Add your custom domain
3. Follow DNS configuration instructions

---

## Alternative Platforms

### Railway

[Railway](https://railway.app) supports both frontend and backend in one project.

```yaml
# railway.toml (backend)
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
```

### Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy backend
cd backend
fly launch

# Deploy frontend
cd ../frontend
fly launch
```

### AWS

| Component | AWS Service |
|-----------|-------------|
| Backend | Lambda + API Gateway or ECS |
| Frontend | S3 + CloudFront |
| Database | RDS (future) |
| Caching | ElastiCache (future) |

### DigitalOcean App Platform

1. Create App from GitHub
2. Configure as monorepo with multiple components
3. Set environment variables
4. Deploy

---

## Environment Configuration

### Required Environment Variables

#### Backend

| Variable | Production Value | Description |
|----------|------------------|-------------|
| `MOCK_MODE` | `false` | Use real external APIs |
| `DEBUG` | `false` | Disable debug logging |

#### Frontend

| Variable | Production Value | Description |
|----------|------------------|-------------|
| `VITE_API_BASE_URL` | Backend URL | API endpoint URL |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CACHE_TTL_BINS` | `3600` | Bin cache TTL (seconds) |
| `CACHE_TTL_PLANNING` | `1800` | Planning cache TTL |
| `CACHE_TTL_AIR_QUALITY` | `600` | Air quality cache TTL |
| `HTTP_TIMEOUT` | `30.0` | External API timeout |

---

## Health Monitoring

### Health Check Endpoints

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `/health` | Liveness check | `{"status": "ok"}` |
| `/` | API info | `{"name": "...", "version": "..."}` |

### Monitoring Setup

#### UptimeRobot (Free)

1. Create account at [uptimerobot.com](https://uptimerobot.com)
2. Add HTTP monitor for `https://your-api.com/health`
3. Configure alerts (email, Slack, etc.)

#### Better Uptime

1. Create monitor for API health endpoint
2. Set 1-minute check interval
3. Configure status page

### Logging

For production, configure structured logging:

```python
# In production, use JSON logging
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        })
```

---

## SSL/TLS Configuration

### Managed Platforms

Render, Vercel, and Railway automatically provide:

- Free SSL certificates (Let's Encrypt)
- Automatic renewal
- HTTPS by default

### Self-Hosted (nginx)

For Docker/VPS deployments, add SSL with Let's Encrypt:

```bash
# Install Certbot
apt-get update
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

Update `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... rest of configuration
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Troubleshooting Deployments

### Backend Issues

#### Container won't start

```bash
# Check logs
docker compose logs backend

# Common issues:
# - Missing environment variables
# - Port already in use
# - Python version mismatch
```

#### Health check failing

1. Verify `/health` endpoint returns 200
2. Check container has enough memory
3. Verify external API connectivity

#### Slow response times

1. Check external API latency
2. Verify caching is working
3. Consider scaling resources

### Frontend Issues

#### Build fails

```bash
# Check build logs
npm run build

# Common issues:
# - TypeScript errors
# - Missing dependencies
# - Environment variable not set
```

#### API calls failing

1. Check `VITE_API_BASE_URL` is correct
2. Verify CORS is configured on backend
3. Check network connectivity

#### 404 on page refresh

For SPA routing, ensure nginx or hosting is configured:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### Common Fixes

| Issue | Solution |
|-------|----------|
| CORS errors | Add frontend URL to backend CORS origins |
| 502 Bad Gateway | Check backend is running and healthy |
| Environment variables not working | Rebuild after changing env vars |
| Stale content | Clear CDN cache |

---

## Deployment Checklist

Before going live:

- [ ] Set `MOCK_MODE=false` for real API data
- [ ] Set `DEBUG=false` to disable debug logs
- [ ] Configure proper CORS origins
- [ ] Set up health monitoring
- [ ] Test all endpoints work
- [ ] Verify frontend can reach backend
- [ ] Check SSL certificate is valid
- [ ] Configure custom domain (optional)
- [ ] Set up logging/alerting
- [ ] Document deployment process

---

## Related Documentation

- [Architecture Overview](./ARCHITECTURE_OVERVIEW.md) - System architecture
- [Backend Structure](./BACKEND_STRUCTURE.md) - Backend details
- [Frontend Structure](./FRONTEND_STRUCTURE.md) - Frontend details
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions
