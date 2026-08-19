from functools import lru_cache

import pandas as pd

from app.config import TRADES_FILE, MARKET_DATA_FILE, RISK_SENSITIVITIES_FILE, FX_RATES_FILE

AS_OF_DATE = pd.Timestamp("2026-08-05")


@lru_cache(maxsize=1)
def load_trades() -> pd.DataFrame:
    df = pd.read_csv(TRADES_FILE)

    before = len(df)
    df = df.drop_duplicates()
    dropped = before - len(df)
    if dropped:
        print(f"[data_loader] {dropped} duplicated lines deleted from trades.csv")

    df["trade_date"] = pd.to_datetime(df["trade_date"], format="mixed")
    df["settle_date"] = pd.to_datetime(df["settle_date"], format="mixed", errors="coerce")
    df["maturity_date"] = pd.to_datetime(df["maturity_date"], format="mixed", errors="coerce")

    return df.reset_index(drop=True)


@lru_cache(maxsize=1)
def load_market_data() -> pd.DataFrame:
    df = pd.read_csv(MARKET_DATA_FILE)
    df["date"] = pd.to_datetime(df["date"])
    df["last_update_utc"] = pd.to_datetime(df["last_update_utc"])
    return df


@lru_cache(maxsize=1)
def load_risk_sensitivities() -> pd.DataFrame:
    df = pd.read_csv(RISK_SENSITIVITIES_FILE)
    df["as_of_date"] = pd.to_datetime(df["as_of_date"])
    return df


@lru_cache(maxsize=1)
def load_fx_rates() -> pd.DataFrame:
    df = pd.read_csv(FX_RATES_FILE)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_latest_market_data() -> pd.DataFrame:
    
    md = load_market_data()
    latest = md[md["date"] == AS_OF_DATE].copy()
    latest["is_stale"] = latest["last_update_utc"].dt.date < AS_OF_DATE.date()
    return latest


def clear_cache():

    load_trades.cache_clear()
    load_market_data.cache_clear()
    load_risk_sensitivities.cache_clear()
    load_fx_rates.cache_clear()
