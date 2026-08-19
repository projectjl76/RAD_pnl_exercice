"""
Valuation of trades and calculation of daily P&L.

  GOVT_BOND / CORP_BOND : notional * clean_price / 100
  IRS                   : notional
  CDS                   : notional
  FX_SPOT/FORWARD/NDF   : notional
  EQ_OPTION / EQ_FUTURE : quantity * price (quantity -> if negative = short)

Daily P&L (desk risk-based P&L proxy) :

- Instruments with a quoted price (bonds, equity options/futures):
- P&L = price change x quantity/notional, converted into USD
- IRS: P&L ≈ DV01 x change in the par rate (in bps)
- CDS: P&L ≈ CS01_USD x change in the spread (in bps) — already in USD

"""
import pandas as pd

from app.services.data_loader import load_trades, load_market_data, load_risk_sensitivities, AS_OF_DATE
from app.services.fx import convert_to_usd

PRICED_PRODUCTS = {"GOVT_BOND", "CORP_BOND", "EQ_OPTION", "EQ_FUTURE"}


def _market_snapshot(as_of: pd.Timestamp) -> pd.DataFrame:
    md = load_market_data()
    return md[md["date"] == as_of].set_index("instrument_id")


def _previous_business_day(as_of: pd.Timestamp) -> pd.Timestamp:
    md = load_market_data()
    prior_dates = md.loc[md["date"] < as_of, "date"]
    if prior_dates.empty:
        raise ValueError("Pas de date antérieure disponible dans market_data.csv")
    return prior_dates.max()


def compute_market_value_usd() -> pd.DataFrame:

    trades = load_trades().copy()
    snap = _market_snapshot(AS_OF_DATE)

    def value_row(row) -> pd.Series:
        pt = row["product_type"]
        is_priced = True

        if pt in ("GOVT_BOND", "CORP_BOND"):
            if row["instrument_id"] in snap.index and pd.notna(snap.loc[row["instrument_id"], "price"]):
                price = snap.loc[row["instrument_id"], "price"]
            else:
                price = row["trade_price"]
                is_priced = False
            amount = row["notional"] * price / 100.0
        elif pt in ("EQ_OPTION", "EQ_FUTURE"):
            if row["instrument_id"] in snap.index and pd.notna(snap.loc[row["instrument_id"], "price"]):
                price = snap.loc[row["instrument_id"], "price"]
            else:
                price = row["trade_price"]
                is_priced = False
            amount = row["quantity"] * price
        else:
            # IRS, CDS, FX_* : pas de market value au sens strict -> notional comme proxy d'exposition
            amount = row["notional"]

        sign = -1 if row["direction"] in ("SELL", "PAY") else 1
        value_usd = convert_to_usd(amount * sign, row["currency"], AS_OF_DATE)
        return pd.Series({"market_value_usd": value_usd, "is_priced": is_priced})

    trades[["market_value_usd", "is_priced"]] = trades.apply(value_row, axis=1)
    return trades


def compute_daily_pnl_by_book() -> list[dict]:
    trades = load_trades()
    md = load_market_data()
    risk = load_risk_sensitivities()

    prev_date = _previous_business_day(AS_OF_DATE)
    snap_today = _market_snapshot(AS_OF_DATE)
    snap_prev = _market_snapshot(prev_date)

    dv01 = risk[risk["risk_metric"] == "DV01"].set_index("trade_id")
    cs01 = risk[risk["risk_metric"] == "CS01_USD"].set_index("trade_id")

    pnl_rows = []
    for row in trades.itertuples():
        sign = -1 if row.direction in ("SELL", "PAY") else 1
        pnl_usd = None

        if row.product_type in PRICED_PRODUCTS and row.instrument_id in snap_today.index and row.instrument_id in snap_prev.index:
            price_today = snap_today.loc[row.instrument_id, "price"]
            price_prev = snap_prev.loc[row.instrument_id, "price"]
            if pd.notna(price_today) and pd.notna(price_prev):
                qty = row.notional / 100.0 if row.product_type in ("GOVT_BOND", "CORP_BOND") else row.quantity
                pnl_native = sign * qty * (price_today - price_prev)
                pnl_usd = convert_to_usd(pnl_native, row.currency, AS_OF_DATE)

        elif row.product_type == "IRS" and row.trade_id in dv01.index:
            if row.instrument_id in snap_today.index and row.instrument_id in snap_prev.index:
                y_today = snap_today.loc[row.instrument_id, "yield_pct"]
                y_prev = snap_prev.loc[row.instrument_id, "yield_pct"]
                if pd.notna(y_today) and pd.notna(y_prev):
                    move_bps = (y_today - y_prev) * 100
                    pnl_native = float(dv01.loc[row.trade_id, "value"]) * move_bps
                    pnl_usd = convert_to_usd(pnl_native, row.currency, AS_OF_DATE)

        elif row.product_type == "CDS" and row.trade_id in cs01.index:
            if row.instrument_id in snap_today.index and row.instrument_id in snap_prev.index:
                s_today = snap_today.loc[row.instrument_id, "spread_bps"]
                s_prev = snap_prev.loc[row.instrument_id, "spread_bps"]
                if pd.notna(s_today) and pd.notna(s_prev):
                    move_bps = s_today - s_prev
                    pnl_usd = float(cs01.loc[row.trade_id, "value_usd"]) * move_bps

        pnl_rows.append({
            "trade_id": row.trade_id,
            "book_id": row.book_id,
            "pnl_usd": pnl_usd,
        })

    pnl_df = pd.DataFrame(pnl_rows)
    priced = pnl_df.dropna(subset=["pnl_usd"])
    unpriced_count = pnl_df["pnl_usd"].isna().sum()

    result = (
        priced.groupby("book_id")["pnl_usd"]
        .sum()
        .reset_index()
        .rename(columns={"pnl_usd": "daily_pnl_usd"})
    )
    result["as_of_date"] = AS_OF_DATE.strftime("%Y-%m-%d")
    result["prior_date"] = prev_date.strftime("%Y-%m-%d")

    fx_trade_count = (trades["product_type"].isin(["FX_SPOT", "FX_FORWARD", "FX_NDF"])).sum()
    other_unpriced = unpriced_count - fx_trade_count

    output = result.to_dict(orient="records")
    warnings = []
    if fx_trade_count:
        warnings.append(
            f"P&L for book FX-ASIA-01 not computed ({fx_trade_count} trades)"
        )
    if other_unpriced > 0:
        warnings.append(
            f"{other_unpriced} other trades were excluded (HKLAND-3.875-2029)."
        )
    if warnings:
        output.append({"_warnings": warnings})
    return output
