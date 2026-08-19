from app.services.data_loader import load_trades
from app.services.valuation import compute_market_value_usd


def get_positions_by_book() -> list[dict]:
    trades = compute_market_value_usd()

    grouped = (
        trades.groupby("book_id")
        .agg(
            trade_count=("trade_id", "count"),
            asset_class=("asset_class", "first"),
            gross_exposure_usd=("market_value_usd", lambda s: s.abs().sum()),
            net_exposure_usd=("market_value_usd", "sum"),
        )
        .reset_index()
    )
    grouped[["gross_exposure_usd", "net_exposure_usd"]] = grouped[
        ["gross_exposure_usd", "net_exposure_usd"]
    ].round(0)

    return grouped.to_dict(orient="records")


def get_trades_for_book(book: str) -> list[dict]:
    trades = compute_market_value_usd()
    subset = trades[trades["book_id"] == book].copy()
    for col in ("trade_date", "settle_date", "maturity_date"):
        subset[col] = subset[col].dt.strftime("%Y-%m-%d")
    return subset.to_dict(orient="records")
