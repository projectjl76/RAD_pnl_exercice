from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

TRADES_FILE = DATA_DIR / "trades.csv"
MARKET_DATA_FILE = DATA_DIR / "market_data.csv"
RISK_SENSITIVITIES_FILE = DATA_DIR / "risk_sensitivities.csv"
FX_RATES_FILE = DATA_DIR / "fx_rates.csv"

REPORTING_CCY = "USD"