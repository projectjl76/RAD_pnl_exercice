from fastapi import APIRouter, HTTPException

from app.services import pnl_service

router = APIRouter()


@router.get("/daily")
def daily_pnl():
    try:
        return pnl_service.get_daily_pnl_by_book()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
