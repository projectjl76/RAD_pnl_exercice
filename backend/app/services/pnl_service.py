from app.services.valuation import compute_daily_pnl_by_book


def get_daily_pnl_by_book() -> list[dict]:
    return compute_daily_pnl_by_book()
