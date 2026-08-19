# Desk Risk & P&L Tool — Exercise

Prototype of a position, P&L, and risk monitoring tool for a cross-asset desk covering **rates, credit, FX, and equity derivatives** in Asia.

---

## Table of Contents

* [Overview](#overview)
* [Stack](#stack)
* [Scope](#scope)
* [Data Quality & Cleaning](#data-quality--cleaning)
* [Getting Started](#getting-started)
* [Technical Choices](#technical-choices)
* [Known Limitations](#known-limitations)
* [Risk Metrics Glossary](#risk-metrics-glossary)
* [Repository Structure](#repository-structure)

---

## Overview

The tool provides a lightweight dashboard for monitoring:

* Trading positions
* USD-converted exposures
* Risk sensitivities
* Daily P&L

The objective is to provide a clear **morning risk view** of the desk while keeping the implementation simple and transparent.

The application covers four books:

* `RATES-ASIA-01`
* `CREDIT-ASIA-01`
* `FX-ASIA-01`
* `EQD-ASIA-01`

---

## Stack

| Component | Technology              |
| --------- | ----------------------- |
| Backend   | Python, FastAPI, pandas |
| Frontend  | TypeScript              |
| Data      | CSV                     |
| API       | REST                    |
| Testing   | pytest                  |

---

## Scope

The application provides three main views.

### Positions

Displays gross and net exposure by book, converted to USD.

### Risk

Displays native risk sensitivities by book:

| Book   | Metrics                   |
| ------ | ------------------------- |
| Rates  | DV01, Duration            |
| Credit | Spread01, CS01, JTD       |
| Equity | Delta, Gamma, Vega, Theta |
| FX     | Delta                     |

Indicative **green / orange / red** thresholds are used to highlight risk levels.

### P&L

Displays daily **risk-based proxy P&L** by book.

---

## Data Quality & Cleaning

The provided `README_datasets.txt` states that **"no further cleansing has been applied"**. This was verified during implementation.

Several data-quality issues were identified and handled.

### Duplicate Trade

`TRD-015` appears twice identically in `trades.csv`.

**Treatment:** deduplicated at load time.

### Inconsistent Date Formats

`trade_date` mixes:

* `YYYY-MM-DD`
* `MM/DD/YYYY`

For example, `TRD-023` and `TRD-034`.

**Treatment:** dates are parsed using a mixed-format parser rather than enforcing a single format.

### Missing Market Data

`HKLAND-3.875-2029` (`TRD-011`) is traded but has no corresponding quote in `market_data.csv`.

**Treatment:**

* execution price is used as a fallback proxy
* `is_priced` is set to `false`
* the application does not fail
* the missing quote is not silently treated as a valid market price

### Stale Market Data

`CDB-3.4-2028` on 05/08 has a `last_update_utc` timestamp from the previous day (04/08).

**Treatment:** the quote is flagged as `is_stale` by:

```text
data_loader.get_latest_market_data()
```

The flag is exposed by the backend but is not yet displayed in the UI.

### Expected NaN Values

`market_data.csv` contains NaN values in:

* `price`
* `yield_pct`
* `spread_bps`
* `implied_vol_pct`

These are expected because each field is only relevant for specific product types.

**Treatment:** no global `fillna(0)` is applied. The relevant market-data field is selected according to the instrument's `product_type`.

---

## Getting Started

### 1. Add the Data

The four provided CSV files are **not committed to the repository**, as required by the exercise.

Place them in the `data/` directory at the project root:

```text
data/
├── trades.csv
├── market_data.csv
├── risk_sensitivities.csv
└── fx_rates.csv
```

---

### 2. Start the Backend

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

The API is available at:

```text
http://localhost:8000
```

Interactive Swagger documentation:

```text
http://localhost:8000/docs
```

### Run Tests

```bash
PYTHONPATH=. pytest app/tests/ -v
```

---

### 3. Start the Frontend

Open a second terminal:

```bash
cd frontend

npm install
npm run dev
```

The application is available at:

```text
http://localhost:5173
```

---

## Technical Choices

### No Frontend Framework

The frontend intentionally does not use React, Angular, or Vue.

For this prototype, the priority was:

* calculation
* transparency
* data quality
* simplicity
* speed of implementation

For a larger production application, a framework would be appropriate for richer state management, reusable components, routing, and more complex UI interactions.

### FastAPI

FastAPI was selected for the backend because it provides:

* strong typing
* automatic API documentation
* straightforward REST API development
* fast development with minimal boilerplate

### Centralized Data Cleaning

All raw-data loading and cleaning is centralized in:

```text
backend/app/services/data_loader.py
```

---

## Known Limitations

### FX P&L Is Not Calculated

The FX book P&L is intentionally excluded.

A correct FX P&L requires revaluing **both legs of each currency pair**, rather than simply applying a price change to the notional in the trade currency.

Rather than producing a potentially misleading number, the FX P&L is explicitly excluded.

### Risk-Based Proxy P&L

The P&L is a **risk-based proxy**, not an exact accounting P&L.

The methodology relies on:

* price changes for bonds and equity instruments
* DV01 for rates
* CS01 for credit

between the two latest available market dates.


### Equity Contract Multipliers

No contract multiplier is currently applied to equity futures/options.

The prototype uses:

```text
quantity × price
```

### Additional Production Features

The following features are not implemented:

* Authentication
* Trader vs. risk-manager permissions
* Position history
* Audit trail
* Real-time WebSocket refresh
* Comprehensive edge-case testing

---

## Risk Metrics Glossary

| Metric        | Book(s)       | Meaning                                               |
| ------------- | ------------- | ----------------------------------------------------- |
| **DV01**      | RATES, CREDIT | Change in value for a 1 bp move in rates              |
| **Duration**  | RATES         | Modified duration, in years                           |
| **Spread01**  | CREDIT        | Change in value for a 1 bp move in spread             |
| **CS01_USD**  | CREDIT        | CDS spread sensitivity for a 1 bp move, in USD        |
| **JTD_USD**   | CREDIT        | Jump-to-default exposure, in USD                      |
| **Delta_USD** | EQUITY, FX    | First-order price sensitivity, in USD                 |
| **Gamma_USD** | EQUITY        | Second-order price sensitivity, in USD                |
| **Vega_USD**  | EQUITY        | Sensitivity to a 1-point change in volatility, in USD |
| **Theta_USD** | EQUITY        | Daily time decay, in USD                              |

---

## Repository Structure

```text
backend/
└── app/
    ├── main.py                    # FastAPI entry point
    ├── config.py                  # Data paths and reporting currency
    │
    ├── routers/                   # API layer
    │   ├── positions
    │   ├── pnl
    │   └── risk
    │
    ├── services/
    │   ├── data_loader.py         # Loading + cleaning of the 4 CSVs
    │   ├── fx.py                  # USD conversion and FX pair direction
    │   ├── valuation.py           # Trade valuation + daily P&L
    │   ├── positions_service.py
    │   ├── pnl_service.py
    │   └── risk_service.py
    │
    └── tests/

frontend/
└── src/
    ├── api/                       # HTTP client + shared types
    ├── views/                     # Positions / P&L / Risk views
    └── main.ts                    # Tab navigation

data/                              # Not committed — provided CSVs
├── trades.csv
├── market_data.csv
├── risk_sensitivities.csv
└── fx_rates.csv
```

---

## Disclaimer

This project is a **prototype for an exercise** and is not intended to be used as a production trading, valuation, or risk-management system.