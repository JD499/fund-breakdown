import logging
from typing import Annotated

import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from yfinance import Ticker

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

TICKER_MAPPINGS = {
    "SMSN": "SMSN.IL",
    "00939": "0939.HK",
    "RIGD": "RIGD.IL",
}


def remap_ticker(ticker):
    mapped_ticker = TICKER_MAPPINGS.get(ticker, ticker)
    if mapped_ticker != ticker:
        logging.info(f"Remapped ticker {ticker} to {mapped_ticker}")
    return mapped_ticker


def get_security_info(ticker: str) -> Ticker:
    ticker = remap_ticker(ticker)

    logging.info(f"Fetching data for {ticker}...")
    security: Ticker = yf.Ticker(ticker)

    fast_info = security.fast_info

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


def get_sector(security):
    sector = security.info.get("sector", "")
    if not sector or pd.isna(sector):
        logging.warning("No sector information found for security")
        return "Unknown"
    return sector


def get_nation(security):
    country = security.info.get("country", "")
    if not country or pd.isna(country):
        return "Unknown"

    return country


def get_etf_sector_breakdown(security):
    if hasattr(security, "funds_data"):
        sector_data = security.funds_data.sector_weightings
        if sector_data is not None:
            return {k.capitalize(): v for k, v in sector_data.items()}


def is_etf(security):
    return security.info.get("quoteType", "").upper() in [
        "ETF",
        "MUTUALFUND",
    ]


def get_holdings_data(etf):
    fund_data = etf.funds_data
    holdings = fund_data.top_holdings.copy()
    holdings = holdings.reset_index()
    holdings = holdings.rename(
        columns={"Symbol": "Ticker", "Holding Percent": "Weight"}
    )

    return holdings


def calculate_look_through(
    ticker: str,
    portfolio_weight: float = 1.0,
):
    security = get_security_info(ticker)

    security_type = "ETF" if is_etf(security) else "Stock"
    security_name = security.info.get("longName", ticker)
    sector = get_sector(security) if security_type == "Stock" else "ETF"
    nation = get_nation(security)

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

    holdings = get_holdings_data(security)
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

    final_holdings = []
    logging.info(
        f"Processing {ticker} ({portfolio_weight:.1f}% of portfolio) with {len(holdings)} holdings..."
    )

    for _, row in holdings.iterrows():
        weight = row["Weight"] * portfolio_weight

        fund_ticker = row["Ticker"]
        logging.info(f"Found fund: {row['Name']} ({fund_ticker})")

        underlying_holdings = calculate_look_through(fund_ticker, weight)

        final_holdings.append(underlying_holdings)

    return pd.concat(final_holdings, ignore_index=True)


def merge_holdings(combined):
    logging.info("Merging holdings...")
    combined["StandardTicker"] = combined["Ticker"]

    merged = (
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


def calculate_portfolio_sector_breakdown(portfolio):
    logging.info("Calculating sector breakdown...")
    sector_weights = {}

    for ticker, weight in portfolio.items():
        security = get_security_info(ticker)
        if security is None:
            continue

        if is_etf(security):
            etf_sectors = get_etf_sector_breakdown(security)
            for sector, sector_weight in etf_sectors.items():
                sector_weights[sector] = sector_weights.get(sector, 0) + (
                    sector_weight * weight
                )
        else:
            sector = get_sector(security)
            sector_weights[sector] = sector_weights.get(sector, 0) + weight

    return sector_weights


def build_portfolio(ticker: list[str], weight: list[str]) -> dict[str, float]:
    if not ticker:
        raise HTTPException(status_code=400, detail="Portfolio is empty")

    portfolio: dict[str, float] = {}
    total_weight: float = 0

    for ticker, weight in zip(ticker, weight):
        ticker = ticker.strip().upper()
        try:
            weight = float(weight)
            if not ticker or weight < 0 or weight > 100:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid weight for {ticker}: {weight}% (must be between 0-100%)",
                )

            portfolio[ticker] = weight
            total_weight += weight

        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid weight value: {weight}"
            )

    if abs(total_weight - 100) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Portfolio weights must sum to 100% (currently {total_weight:.2f}%)",
        )

    logging.info("Portfolio built successfully")
    return portfolio


@app.get("/", response_class=FileResponse)
def home():
    logging.info("Serving home page")
    return "index.html"


@app.post("/analyze")
async def analyze(
    ticker: Annotated[list[str], Form()], weight: Annotated[list[str], Form()]
):
    logging.info("Processing analysis request")

    portfolio = build_portfolio(ticker, weight)

    all_holdings = []
    for ticker, weight in portfolio.items():
        holdings = calculate_look_through(ticker, weight)
        if not holdings.empty:
            all_holdings.append(holdings)

    if not all_holdings:
        logging.warning("No holdings data available")
        return {"error": "No holdings data available"}

    combined = pd.concat(all_holdings, ignore_index=True)
    merged = merge_holdings(combined)
    holdings_data = merged.head(50).to_dict(orient="records")

    sector_breakdown = calculate_portfolio_sector_breakdown(portfolio)

    logging.info("Analysis complete")
    return {"holdings": holdings_data, "sectors": sector_breakdown}
