from fastapi import FastAPI
from routers import bins, planning, air_quality

app = FastAPI(title="Local Council Data Explorer")

app.include_router(bins.router, prefix="/api/bins", tags=["bins"])
app.include_router(planning.router, prefix="/api/planning", tags=["planning"])
app.include_router(air_quality.router, prefix="/api/air-quality", tags=["air_quality"])


@app.get("/health")
def health():
    return {"status": "ok"}
