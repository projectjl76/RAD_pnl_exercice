from fastapi import APIRouter, HTTPException

from app.services import positions_service

router = APIRouter()


@router.get("/")
def list_positions_by_book():
    try:
        return positions_service.get_positions_by_book()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{book}/trades")
def list_trades_for_book(book: str):
    return positions_service.get_trades_for_book(book)
