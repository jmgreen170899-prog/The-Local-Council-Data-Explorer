from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_planning(lpa: str = "", date_from: str = "", date_to: str = ""):
    return {
        "lpa": lpa or "Example Council",
        "applications": [
            {
                "reference": "23/12345/FU",
                "address": "12 Example Road",
                "proposal": "Rear extension",
                "status": "Pending",
                "received_date": "2025-11-10"
            }
        ]
    }
