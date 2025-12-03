"""
Main application entry point for the Local Council Data Explorer API.

This FastAPI application provides endpoints for:
- Bin collection schedules
- Planning applications
- Air quality data

The application includes CORS middleware for cross-origin requests,
comprehensive OpenAPI documentation, and health check endpoints.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import bins, planning, air_quality

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} API")
    logger.info(f"Mock mode: {settings.MOCK_MODE}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    yield
    # Shutdown
    logger.info("Shutting down API")


# Create FastAPI application with comprehensive metadata
app = FastAPI(
    title="Local Council Data Explorer API",
    description="""
    **A RESTful API for UK local council data including bin collections, 
    planning applications, and air quality information.**

    ## Features

    - **Bin Collections**: Retrieve bin collection schedules by postcode or UPRN
    - **Planning Applications**: Search planning applications by Local Planning Authority
    - **Air Quality**: Get current DAQI readings and pollutant breakdowns

    ## Data Sources

    - City of York Council Waste API
    - planning.data.gov.uk
    - UK-AIR Defra API

    ## Caching

    All endpoints implement intelligent caching to reduce external API load:
    - Bin collections: 1 hour TTL
    - Planning data: 30 minutes TTL
    - Air quality: 10 minutes TTL
    """,
    version=settings.API_VERSION,
    contact={
        "name": "Local Council Data Explorer",
        "url": "https://github.com/your-username/local-council-data-explorer",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Configure CORS middleware for cross-origin requests
# In production, restrict origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Add production domains here
        # "https://your-frontend-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bins.router, prefix="/api", tags=["Bin Collections"])
app.include_router(planning.router, prefix="/api", tags=["Planning Applications"])
app.include_router(
    air_quality.router, prefix="/api", tags=["Air Quality"]
)


@app.get("/health", tags=["Health"])
def health():
    """
    Health check endpoint.

    Returns the current health status of the API.
    Use this endpoint for load balancer health checks and monitoring.
    """
    return {"status": "ok", "version": settings.API_VERSION}


@app.get("/", tags=["Health"])
def root():
    """
    Root endpoint with API information.

    Provides basic information about the API and links to documentation.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
