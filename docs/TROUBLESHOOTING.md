# Troubleshooting Guide

> Solutions for common issues when developing, building, and running the Local Council Data Explorer.

---

## Table of Contents

- [Development Issues](#development-issues)
- [Build Issues](#build-issues)
- [Docker Issues](#docker-issues)
- [API Issues](#api-issues)
- [Frontend Issues](#frontend-issues)
- [Deployment Issues](#deployment-issues)
- [Performance Issues](#performance-issues)
- [FAQ](#faq)

---

## Development Issues

### Backend won't start

**Symptom**: `uvicorn main:app --reload` fails or crashes

**Solutions**:

1. **Virtual environment not activated**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

2. **Dependencies not installed**
   ```bash
   pip install -r requirements.txt
   ```

3. **Port already in use**
   ```bash
   # Find process using port 8000
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   
   # Kill the process or use different port
   uvicorn main:app --reload --port 8001
   ```

4. **Python version mismatch**
   ```bash
   # Check Python version (requires 3.11+)
   python --version
   ```

---

### Frontend won't start

**Symptom**: `npm run dev` fails

**Solutions**:

1. **Node modules not installed**
   ```bash
   npm install
   ```

2. **Clear npm cache**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Port already in use**
   ```bash
   # Vite will auto-select another port, or specify:
   npm run dev -- --port 3000
   ```

4. **Node version too old**
   ```bash
   # Check Node version (requires 20+)
   node --version
   ```

---

### API calls failing in development

**Symptom**: Frontend shows network errors or CORS issues

**Solutions**:

1. **Backend not running**
   ```bash
   # Start backend first
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Vite proxy not configured**
   
   Check `vite.config.ts`:
   ```typescript
   server: {
     proxy: {
       "/api": {
         target: "http://localhost:8000",
         changeOrigin: true,
       },
     },
   }
   ```

3. **Wrong API URL in code**
   
   Check `src/api/client.ts`:
   ```typescript
   export const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";
   ```

---

## Build Issues

### TypeScript compilation errors

**Symptom**: `npm run build` fails with type errors

**Solutions**:

1. **Fix type errors**
   ```bash
   # Run type checker to see all errors
   npx tsc --noEmit
   ```

2. **Common type fixes**:
   - Add proper type annotations
   - Use `unknown` instead of `any`
   - Check for null/undefined

3. **Update TypeScript**
   ```bash
   npm update typescript
   ```

---

### Python tests failing

**Symptom**: `pytest` reports failures

**Solutions**:

1. **Install test dependencies**
   ```bash
   pip install pytest pytest-asyncio
   ```

2. **Run specific test for debugging**
   ```bash
   pytest tests/test_bins_service.py -v
   ```

3. **Check mock mode is enabled**
   
   Tests may require `MOCK_MODE=true`

---

## Docker Issues

### Container won't start

**Symptom**: `docker compose up` fails or container exits

**Solutions**:

1. **Check logs**
   ```bash
   docker compose logs backend
   docker compose logs frontend
   ```

2. **Rebuild containers**
   ```bash
   docker compose down
   docker compose up --build
   ```

3. **Verify Dockerfile**
   
   Check for:
   - Correct base image
   - Proper COPY paths
   - Valid CMD/ENTRYPOINT

---

### Health check failing

**Symptom**: Container shows as `unhealthy`

**Solutions**:

1. **Check if service is responding**
   ```bash
   # From host
   curl http://localhost:8000/health
   
   # From inside container
   docker compose exec backend curl http://localhost:8000/health
   ```

2. **Increase health check timeout**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
     interval: 30s
     timeout: 10s  # Increase if needed
     retries: 5    # Increase retries
     start_period: 30s  # Allow more startup time
   ```

3. **Check container resources**
   ```bash
   docker stats
   ```

---

### Frontend can't reach backend in Docker

**Symptom**: API calls fail in containerized environment

**Solutions**:

1. **Check network configuration**
   
   Both containers must be on same network:
   ```yaml
   networks:
     - council-network
   ```

2. **Verify VITE_API_BASE_URL**
   
   For Docker, should be empty (nginx proxies):
   ```yaml
   args:
     - VITE_API_BASE_URL=
   ```

3. **Check nginx proxy configuration**
   ```nginx
   location /api/ {
       proxy_pass http://backend:8000;
   }
   ```

---

## API Issues

### External API timeouts

**Symptom**: 503 errors, "Service timed out"

**Solutions**:

1. **Use mock mode for development**
   ```bash
   export MOCK_MODE=true
   ```

2. **Increase timeout**
   ```python
   # In config.py
   HTTP_TIMEOUT: float = 60.0  # Increase from 30
   ```

3. **Check external API status**
   - City of York API: May have maintenance windows
   - planning.data.gov.uk: Check service status
   - UK-AIR: May have rate limits

---

### Cache not working

**Symptom**: Same data returned even after TTL expires

**Solutions**:

1. **Check cache configuration**
   ```python
   CACHE_TTL_BINS: int = 3600  # 1 hour
   ```

2. **Verify cache key generation**
   ```python
   # Debug cache keys
   logger.debug(f"Cache key: {cache_key}")
   ```

3. **Clear cache (restart service)**
   
   In-memory cache clears on restart.

---

### Missing or incorrect data

**Symptom**: API returns empty or wrong data

**Solutions**:

1. **Check mock data**
   
   Only certain postcodes/LPAs are mocked:
   - `YO1 1AA`, `SW1A 1AA`, `M1 1AA`
   - `City of York Council`, `Westminster`

2. **Verify query parameters**
   ```bash
   # Test directly
   curl "http://localhost:8000/api/bins?postcode=YO1%201AA"
   ```

3. **Check data transformation**
   
   Review service layer transformations.

---

## Frontend Issues

### Components not rendering

**Symptom**: Blank page or missing components

**Solutions**:

1. **Check browser console**
   
   Look for JavaScript errors.

2. **Verify data flow**
   ```typescript
   // Add logging to see data
   console.log("Data:", data);
   console.log("Loading:", loading);
   console.log("Error:", error);
   ```

3. **Check conditional rendering**
   ```typescript
   if (loading) return <LoadingState />;
   if (error) return <ErrorState />;
   if (!data) return <EmptyState />;
   ```

---

### Charts not displaying

**Symptom**: Chart area is blank

**Solutions**:

1. **Check data format**
   
   Recharts requires specific data shapes.

2. **Verify ResponsiveContainer**
   
   Parent must have explicit height:
   ```typescript
   <div style={{ height: 300 }}>
     <ResponsiveContainer>
       <BarChart data={data}>...</BarChart>
     </ResponsiveContainer>
   </div>
   ```

3. **Check for null values**
   
   Handle missing data gracefully.

---

### Styles not applying

**Symptom**: Components look unstyled

**Solutions**:

1. **Check CSS imports**
   ```typescript
   // In App.tsx
   import "./App.css";
   ```

2. **Verify class names**
   
   CSS uses kebab-case: `.card-header`
   
   JSX uses camelCase: `className="card-header"`

3. **Check for CSS specificity issues**
   
   Use browser DevTools to inspect.

---

## Deployment Issues

### Render deployment fails

**Symptom**: Build or deploy fails on Render

**Solutions**:

1. **Check build logs in Render dashboard**

2. **Verify requirements.txt**
   ```bash
   # Test locally
   pip install -r requirements.txt
   ```

3. **Check Python version**
   
   Render uses Python 3.x by default.

---

### Vercel build fails

**Symptom**: Frontend build fails on Vercel

**Solutions**:

1. **Check build command**
   ```
   npm run build
   ```

2. **Verify environment variables are set**

3. **Check Node version**
   
   Add to `package.json`:
   ```json
   "engines": {
     "node": ">=20"
   }
   ```

---

### CORS errors in production

**Symptom**: API calls blocked by CORS

**Solutions**:

1. **Add frontend URL to CORS origins**
   ```python
   # In main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://your-frontend.vercel.app",
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Verify API URL in frontend**
   
   Check `VITE_API_BASE_URL` environment variable.

---

## Performance Issues

### Slow API responses

**Symptoms**: High latency, timeouts

**Solutions**:

1. **Check external API latency**
   ```python
   import time
   start = time.time()
   # API call
   logger.info(f"API call took {time.time() - start}s")
   ```

2. **Verify caching is working**
   
   Second request should be faster.

3. **Consider connection pooling**
   
   Use single httpx client instance.

---

### High memory usage

**Symptom**: Container OOM or slow performance

**Solutions**:

1. **Monitor container resources**
   ```bash
   docker stats
   ```

2. **Clear cache periodically**
   ```python
   # Add cache cleanup
   cache.cleanup()
   ```

3. **Increase container memory limit**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 1G
   ```

---

## FAQ

### How do I run without Docker?

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### How do I use real APIs instead of mock data?

Set `MOCK_MODE=false` in backend environment.

### How do I add a new council/postcode to mock data?

Edit the mock data in the service files:
- `backend/services/bins_service.py`
- `backend/services/planning_service.py`
- `backend/services/air_service.py`

### Where are logs stored?

Logs are written to stdout. In Docker:
```bash
docker compose logs -f backend
```

### How do I reset everything?

```bash
# Full cleanup
docker compose down -v --rmi all
rm -rf backend/.venv backend/__pycache__
rm -rf frontend/node_modules frontend/dist

# Fresh start
# ... follow setup instructions
```

---

## Getting Help

If you can't find a solution:

1. Check existing GitHub issues
2. Search error messages online
3. Open a new GitHub issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, versions)

---

## Related Documentation

- [Architecture Overview](./ARCHITECTURE_OVERVIEW.md) - System architecture
- [Backend Structure](./BACKEND_STRUCTURE.md) - Backend details
- [Frontend Structure](./FRONTEND_STRUCTURE.md) - Frontend details
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Deployment instructions
