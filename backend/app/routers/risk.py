from fastapi import APIRouter, HTTPException

from app.services import risk_service

router = APIRouter()


@router.get("/")
def risk_by_book():
    try:
        return risk_service.get_risk_by_book()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
