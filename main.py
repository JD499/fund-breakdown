import logging
from typing import Annotated, Dict, List, Optional, Union, Any
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pandas import DataFrame
from yfinance import Ticker

app: FastAPI = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

TICKER_MAPPINGS: Dict[str, str] = {
    "SMSN": "SMSN.IL",
    "00939": "0939.HK",
    "RIGD": "RIGD.IL",
}


def remap_ticker(ticker: str) -> str:
    mapped_ticker: str = TICKER_MAPPINGS.get(ticker, ticker)
    if mapped_ticker != ticker:
        logging.info(f"Remapped ticker {ticker} to {mapped_ticker}")
    return mapped_ticker


def get_security_info(ticker: str) -> Ticker:
    ticker = remap_ticker(ticker)

    logging.info(f"Fetching data for {ticker}...")
    security: Ticker = yf.Ticker(ticker)

    fast_info: Dict[str, Any] = security.fast_info

    try:
        if fast_info["lastPrice"] == 0:
            logging.error(f"Could not verify price data for {ticker}")
            raise HTTPException(
                status_code=400,
                detail=f"Could not verify price data for {ticker}",
            )
    except (KeyError, AttributeError):
        logging.error(f"Could not verify price data for {ticker}")
        raise HTTPException(
            status_code=400,
            detail=f"Could not verify price data for {ticker}",
        )

    return security


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


def is_etf(security: Ticker) -> bool:
    return security.info.get("quoteType", "").upper() in [
        "ETF",
        "MUTUALFUND",
    ]


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

    security_type: str = "ETF" if is_etf(security) else "Stock"
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

        if is_etf(security):
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


@app.get("/", response_class=FileResponse)
def home() -> Any:
    logging.info("Serving home page")
    return "index.html"


@app.post("/analyze")
async def analyze(
    ticker: Annotated[List[str], Form()], weight: Annotated[List[str], Form()]
) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, float]]]:
    logging.info("Processing analysis request")

    portfolio: Dict[str, float] = build_portfolio(ticker, weight)

    all_holdings: List[DataFrame] = []
    for ticker, weight in portfolio.items():
        holdings: DataFrame = calculate_look_through(ticker, weight)
        if not holdings.empty:
            all_holdings.append(holdings)

    combined: DataFrame = pd.concat(all_holdings, ignore_index=True)
    merged: DataFrame = merge_holdings(combined)
    holdings_data: List[Dict[str, Any]] = merged.head(50).to_dict(orient="records")

    sector_breakdown: Dict[str, float] = calculate_portfolio_sector_breakdown(portfolio)

    logging.info("Analysis complete")
    return {"holdings": holdings_data, "sectors": sector_breakdown}
