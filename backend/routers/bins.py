from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_bins(postcode: str = "", uprn: str = ""):
    # Placeholder response until real API wired in
    return {
        "address": "10 Example Street",
        "council": "City of York",
        "bins": [
            {"type": "Refuse", "collection_date": "2025-12-09"},
            {"type": "Recycling", "collection_date": "2025-12-16"}
        ]
    }
