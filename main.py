import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Annotated, Dict, List, Optional, Any
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pandas import DataFrame
from yfinance import Ticker
from fastapi.templating import Jinja2Templates

DATABASE_NAME = "securities_cache.db"
CACHE_EXPIRY_DAYS = 1

TICKER_MAPPINGS: Dict[str, str] = {
    "SMSN": "SMSN.IL",
    "00939": "0939.HK",
    "RIGD": "RIGD.IL",
}


class CachedTicker:
    def __init__(self, ticker_data: Dict):
        self.info = ticker_data["info"]

        self.fast_info = ticker_data["fast_info"]

        if ticker_data["funds_data"]:
            self.funds_data = type("FundsData", (), {})()

            self.funds_data.sector_weightings = ticker_data["funds_data"].get(
                "sector_weightings"
            )

            holdings_data = ticker_data["funds_data"].get("top_holdings")

            holdings_df = pd.DataFrame(holdings_data["data"])

            self.funds_data.top_holdings = holdings_df


def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)


def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS securities (
                ticker TEXT PRIMARY KEY,
                info JSON,
                fast_info JSON,
                funds_data JSON,
                last_updated TIMESTAMP
            )
        """)
        conn.commit()


def serialize_fast_info(fast_info: Any) -> Dict:
    result = {}
    for key in dir(fast_info):
        if key.startswith("_"):
            continue

        value = getattr(fast_info, key)

        if callable(value):
            continue

        result[key] = value

    return result


def is_fund(security: Ticker) -> bool:
    return security.info.get("quoteType", "").upper() in [
        "ETF",
        "MUTUALFUND",
    ]


def serialize_funds_data(security: Ticker) -> Optional[Dict]:
    funds_data = {"sector_weightings": security.funds_data.sector_weightings}

    holdings_df = security.funds_data.top_holdings

    holdings_df = holdings_df.reset_index()

    column_mapping = {"Symbol": "Ticker", "Holding Percent": "Weight"}

    holdings_df = holdings_df.rename(columns=column_mapping)

    funds_data["top_holdings"] = {
        "data": holdings_df.to_dict(orient="records"),
        "columns": list(holdings_df.columns),
    }

    return funds_data


def get_cached_security(ticker: str) -> Optional[Dict]:
    with get_db_connection() as conn:
        result = conn.execute(
            """
            SELECT info, fast_info, funds_data, last_updated 
            FROM securities 
            WHERE ticker = ?
            """,
            (ticker,),
        ).fetchone()

        if result:
            info, fast_info, funds_data, last_updated = result
            last_updated = datetime.fromisoformat(last_updated)

            if datetime.now() - last_updated < timedelta(days=CACHE_EXPIRY_DAYS):
                return {
                    "info": json.loads(info),
                    "fast_info": json.loads(fast_info),
                    "funds_data": json.loads(funds_data) if funds_data else None,
                }
    return None


def cache_security(ticker: str, security: Ticker):
    try:
        with get_db_connection() as conn:
            info_data = security.info if security.info else {}
            fast_info_data = serialize_fast_info(security.fast_info)
            funds_data = serialize_funds_data(security) if is_fund(security) else None

            conn.execute(
                """
                INSERT OR REPLACE INTO securities (ticker, info, fast_info, funds_data, last_updated)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ticker,
                    json.dumps(info_data),
                    json.dumps(fast_info_data),
                    None if funds_data is None else json.dumps(funds_data),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            logging.info(f"Successfully cached data for {ticker}")
    except Exception as e:
        logging.error(f"Error caching security data for {ticker}: {e}")


def remap_ticker(ticker: str) -> str:
    mapped_ticker: str = TICKER_MAPPINGS.get(ticker, ticker)
    if mapped_ticker != ticker:
        logging.info(f"Remapped ticker {ticker} to {mapped_ticker}")
    return mapped_ticker


def get_security_info(ticker: str) -> CachedTicker | Ticker:
    ticker = remap_ticker(ticker)

    cached_data = get_cached_security(ticker)
    if cached_data:
        logging.info(f"Retrieved {ticker} from cache")
        return CachedTicker(cached_data)

    logging.info(f"Fetching {ticker} from yfinance...")
    security: Ticker = yf.Ticker(ticker)

    try:
        if security.fast_info["lastPrice"] == 0:
            logging.error(f"Could not verify price data for {ticker}")
            raise HTTPException(
                status_code=400,
                detail=f"Could not verify price data for {ticker}",
            )
        cache_security(ticker, security)
        return security

    except (KeyError, AttributeError):
        logging.error(f"Could not verify price data for {ticker}")
        raise HTTPException(
            status_code=400,
            detail=f"Could not verify price data for {ticker}",
        )


def get_sector(security: Ticker) -> str:
    sector: Optional[str] = security.info.get("sector", "")
    if not sector or pd.isna(sector):
        logging.warning("No sector information found for security")
        return "Unknown"
    return sector


def get_nation(security: Ticker) -> str:
    country: Optional[str] = security.info.get("country", "")
    if not country or pd.isna(country):
        return "Unknown"

    return country


def get_etf_sector_breakdown(security: Ticker) -> Optional[Dict[str, float]]:
    if hasattr(security, "funds_data"):
        sector_data: Optional[Dict[str, float]] = security.funds_data.sector_weightings
        if sector_data is not None:
            return {k.capitalize(): v for k, v in sector_data.items()}
    return None


def get_holdings_data(etf: Ticker) -> DataFrame:
    fund_data: Any = etf.funds_data
    holdings: DataFrame = fund_data.top_holdings.copy()
    holdings = holdings.reset_index()
    holdings = holdings.rename(
        columns={"Symbol": "Ticker", "Holding Percent": "Weight"}
    )

    return holdings


def calculate_look_through(
    ticker: str,
    portfolio_weight: float = 1.0,
) -> DataFrame:
    security: Ticker = get_security_info(ticker)

    security_type: str = "ETF" if is_fund(security) else "Stock"
    security_name: str = security.info.get("longName", ticker)
    sector: str = get_sector(security) if security_type == "Stock" else "ETF"
    nation: str = get_nation(security)

    if security_type == "Stock":
        logging.info(
            f"Processing stock: {ticker} ({portfolio_weight:.1f}% of portfolio)"
        )
        return pd.DataFrame(
            {
                "Name": [security_name],
                "Ticker": [ticker],
                "Weight": [portfolio_weight],
                "Type": ["Stock"],
                "Sector": [sector],
                "Nation": [nation],
                "DirectHolding": [True],
            }
        )

    holdings: DataFrame = get_holdings_data(security)
    if holdings.empty:
        logging.warning(f"No holdings data available for {ticker}")
        return pd.DataFrame(
            {
                "Name": [security_name],
                "Ticker": [ticker],
                "Weight": [portfolio_weight],
                "Type": ["ETF"],
                "Sector": ["ETF"],
                "Nation": [nation],
                "DirectHolding": [True],
            }
        )

    final_holdings: List[DataFrame] = []
    logging.info(
        f"Processing {ticker} ({portfolio_weight:.1f}% of portfolio) with {len(holdings)} holdings..."
    )

    for _, row in holdings.iterrows():
        weight: float = row["Weight"] * portfolio_weight

        fund_ticker: str = row["Ticker"]
        logging.info(f"Found fund: {row['Name']} ({fund_ticker})")

        underlying_holdings: DataFrame = calculate_look_through(fund_ticker, weight)

        final_holdings.append(underlying_holdings)

    return pd.concat(final_holdings, ignore_index=True)


def merge_holdings(combined: DataFrame) -> DataFrame:
    logging.info("Merging holdings...")
    combined["StandardTicker"] = combined["Ticker"]

    merged: DataFrame = (
        combined.groupby("StandardTicker")
        .agg(
            {
                "Name": "first",
                "Ticker": "first",
                "Type": "first",
                "Sector": "first",
                "Nation": "first",
                "Weight": "sum",
                "DirectHolding": "any",
            }
        )
        .reset_index()
    )

    merged = merged.sort_values("Weight", ascending=False)

    return merged


def calculate_portfolio_sector_breakdown(
    portfolio: Dict[str, float],
) -> Dict[str, float]:
    logging.info("Calculating sector breakdown...")
    sector_weights: Dict[str, float] = {}

    for ticker, weight in portfolio.items():
        security: Optional[Ticker] = get_security_info(ticker)
        if security is None:
            continue

        if is_fund(security):
            etf_sectors: Optional[Dict[str, float]] = get_etf_sector_breakdown(security)
            if etf_sectors:
                for sector, sector_weight in etf_sectors.items():
                    sector_weights[sector] = sector_weights.get(sector, 0) + (
                        sector_weight * weight
                    )
        else:
            sector: str = get_sector(security)
            sector_weights[sector] = sector_weights.get(sector, 0) + weight

    return sector_weights


def build_portfolio(ticker: List[str], weight: List[str]) -> Dict[str, float]:
    if not ticker:
        raise HTTPException(status_code=400, detail="Portfolio is empty")

    portfolio: Dict[str, float] = {}
    total_weight: float = 0

    for t, w in zip(ticker, weight):
        t = t.strip().upper()
        try:
            w_float: float = float(w)
            if not t or w_float < 0 or w_float > 100:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid weight for {t}: {w_float}% (must be between 0-100%)",
                )

            portfolio[t] = w_float
            total_weight += w_float

        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid weight value: {w}")

    if abs(total_weight - 100) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Portfolio weights must sum to 100% (currently {total_weight:.2f}%)",
        )

    logging.info("Portfolio built successfully")
    return portfolio


app: FastAPI = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
init_db()


class PortfolioRow:
    def __init__(self, ticker: str = "", weight: float = None):
        self.ticker = ticker
        self.weight = weight


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    rows = [PortfolioRow()]
    return templates.TemplateResponse("index.html", {"request": request, "rows": rows})


@app.post("/add-row")
async def add_row(request: Request):

    form_data = await request.form()
    print(form_data)
    existing_tickers = form_data.getlist("ticker")
    existing_weights = form_data.getlist("weight")


    rows = []
    for t, w in zip(existing_tickers, existing_weights):
        try:
            weight = float(w) if w.strip() else None
            rows.append(PortfolioRow(t, weight))
        except ValueError:

            rows.append(PortfolioRow(t, None))

    rows.append(PortfolioRow())

    return templates.TemplateResponse(
        "partials/tbody.html", {"request": request, "rows": rows}
    )


@app.post("/remove-row/{index}")
async def remove_row(request: Request, index: int):
    form_data = await request.form()
    existing_tickers = form_data.getlist("ticker")
    existing_weights = form_data.getlist("weight")


    if 0 <= index < len(existing_tickers):
        existing_tickers.pop(index)
        existing_weights.pop(index)

    rows = []
    for t, w in zip(existing_tickers, existing_weights):
        try:
            weight = float(w) if w.strip() else None
            rows.append(PortfolioRow(t, weight))
        except ValueError:

            rows.append(PortfolioRow(t, None))

    if not rows:
        rows = [PortfolioRow()]

    return templates.TemplateResponse(
        "partials/tbody.html", {"request": request, "rows": rows}
    )


@app.post("/analyze")
async def analyze(
    request: Request,
    ticker: Annotated[List[str], Form()],
    weight: Annotated[List[float], Form()],
):

    try:
        portfolio: Dict[str, float] = build_portfolio(ticker, weight)


        all_holdings: List[DataFrame] = []
        for ticker, weight in portfolio.items():
            holdings: DataFrame = calculate_look_through(ticker, weight)
            if not holdings.empty:
                all_holdings.append(holdings)

        combined: DataFrame = pd.concat(all_holdings, ignore_index=True)
        merged: DataFrame = merge_holdings(combined)
        holdings_data: List[Dict[str, Any]] = merged.head(50).to_dict(orient="records")


        sector_breakdown: Dict[str, float] = calculate_portfolio_sector_breakdown(
            portfolio
        )


        return templates.TemplateResponse(
            "partials/analysis_results.html",
            {
                "request": request,
                "holdings": holdings_data,
                "sectors": sector_breakdown,
            },
        )
    except Exception as e:
        print("Error in analyze:", str(e))
        raise
