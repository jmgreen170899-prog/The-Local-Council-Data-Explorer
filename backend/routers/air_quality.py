from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_air_quality(area: str = ""):
    return {
        "area": area or "Yorkshire & Humber",
        "max_daqi": 2,
        "summary": "Low",
        "pollutants": [
            {"name": "NO2", "value": 18, "units": "ug/m3"},
            {"name": "PM2.5", "value": 6, "units": "ug/m3"}
        ]
    }
