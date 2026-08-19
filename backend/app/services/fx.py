from functools import lru_cache

import pandas as pd

from app.services.data_loader import load_fx_rates

REPORTING_CCY = "USD"


@lru_cache(maxsize=1)
def _fx_indexed():
    fx = load_fx_rates()
    return fx.set_index(["date", "base_ccy", "quote_ccy"])["spot_rate"]


def get_fx_rate_to_usd(currency: str, as_of_date: pd.Timestamp) -> float:

    if currency == REPORTING_CCY:
        return 1.0

    fx = load_fx_rates()
    day = fx[fx["date"] == as_of_date]

    # Case 1: the currency is the base_ccy and USD is the quote_ccy (EURUSD, AUDUSD)
    #          spot_rate is already "USD per 1 unit of currency".
    as_base = day[(day["base_ccy"] == currency) & (day["quote_ccy"] == REPORTING_CCY)]
    if not as_base.empty:
        return float(as_base.iloc[0]["spot_rate"])

    # Case 2: USD is the base_ccy and the currency is the quote_ccy (USDJPY, USDSGD...)
    #         spot_rate is "currency per 1 USD", so we invert it.
    as_quote = day[(day["base_ccy"] == REPORTING_CCY) & (day["quote_ccy"] == currency)]
    if not as_quote.empty:
        return 1.0 / float(as_quote.iloc[0]["spot_rate"])

    #  use the latest known rate before this date (public holiday, market closed...)
    prior = fx[fx["date"] < as_of_date]
    for base, quote, invert in [(currency, REPORTING_CCY, False), (REPORTING_CCY, currency, True)]:
        match = prior[(prior["base_ccy"] == base) & (prior["quote_ccy"] == quote)].sort_values("date")
        if not match.empty:
            rate = float(match.iloc[-1]["spot_rate"])
            return (1.0 / rate) if invert else rate

    raise ValueError(f"No FX Rate found to convert {currency} in USD at this date : {as_of_date.date()}")


def convert_to_usd(amount: float, currency: str, as_of_date: pd.Timestamp) -> float:
    return amount * get_fx_rate_to_usd(currency, as_of_date)
