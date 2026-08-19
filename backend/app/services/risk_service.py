"""
  RATES  -> DV01, Duration
  CREDIT -> Spread01, CS01_USD, JTD_USD
  EQUITY -> Delta_USD, Gamma_USD, Vega_USD, Theta_USD
  FX     -> Delta_USD

"""
from app.services.data_loader import load_risk_sensitivities

RISK_THRESHOLDS_USD = {
    "DV01": {"warning": 3_000, "breach": 6_000},
    "Spread01": {"warning": 3_000, "breach": 6_000},
    "CS01_USD": {"warning": 5_000, "breach": 10_000},
    "JTD_USD": {"warning": 3_000_000, "breach": 6_000_000},
    "Delta_USD": {"warning": 8_000_000, "breach": 12_000_000},
    "Vega_USD": {"warning": 50_000, "breach": 100_000},
}


def _status(metric: str, value: float) -> str:
    thresholds = RISK_THRESHOLDS_USD.get(metric)
    if not thresholds:
        return "n/a"
    abs_value = abs(value)
    if abs_value >= thresholds["breach"]:
        return "breach"
    if abs_value >= thresholds["warning"]:
        return "warning"
    return "ok"


def get_risk_by_book() -> list[dict]:
    risk = load_risk_sensitivities()
    
    pivot = (
        risk[risk["risk_metric"] != "Duration"]
        .pivot_table(index="book_id", columns="risk_metric", values="value_usd", aggfunc="sum", fill_value=0)
        .reset_index()
    )

    rows = pivot.to_dict(orient="records")
    for row in rows:
        row["_status"] = {
            metric: _status(metric, value)
            for metric, value in row.items()
            if metric not in ("book_id",)
        }
    return rows
