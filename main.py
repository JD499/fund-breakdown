import logging
from time import sleep
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
            if pd.isna(fast_info["lastPrice"]) or fast_info["lastPrice"] == 0:
                logging.error(f"{ticker} has no valid price data")
                raise ValueError(f"No valid price data for {ticker}")
        except (KeyError, AttributeError):
            logging.error(f"Could not verify price data for {ticker}")
            raise ValueError(f"Could not verify price data for {ticker}")
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

    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {str(e)}")
        raise ValueError(f"Failed to process {ticker}: {str(e)}")


def get_sector(security):
    try:
        sector = security.info.get("sector", "")
        if not sector or pd.isna(sector):
            sector = security.info.get("industry", "Unknown")
        if not sector or pd.isna(sector):
            logging.warning(f"No sector information found for security")
            return "Unknown"
        return sector
    except:
        logging.warning(f"Error getting sector information")
        return "Unknown"


def get_nation(security):
    try:
        country = security.info.get("country", "")

        if not country or pd.isna(country):
            return "Unknown"

        return country
    except:
        logging.warning(f"Error getting country information")
        return "Unknown"


def get_etf_sector_breakdown(security):
    try:
        if hasattr(security, "funds_data"):
            sector_data = security.funds_data.sector_weightings
            if sector_data is not None:
                return {k.capitalize(): v for k, v in sector_data.items()}
    except:
        logging.warning(f"Error getting ETF sector breakdown")
    return {}


def standardize_ticker(ticker):
    if pd.isna(ticker):
        return ""
    standard = str(ticker).upper().split(".")[0]
    replacements = {"ADR": "", "CLASS": "C", "ORDINARY": "", "SHARES": ""}
    for old, new in replacements.items():
        standard = standard.replace(old, new)
    return standard.strip()


def is_etf(security):
    try:
        return security.info.get("quoteType", "").upper() in [
            "ETF",
            "MUTUALFUND",
        ] or any(
            keyword in security.info.get("longName", "").upper()
            for keyword in ["ETF", "FUND", "TRUST"]
        )
    except:
        logging.warning(f"Error determining if security is ETF")
        return False


def get_holdings_data(etf):
    try:
        fund_data = etf.funds_data
        if hasattr(fund_data, "top_holdings") and fund_data.top_holdings is not None:
            holdings = fund_data.top_holdings.copy()
            holdings = holdings.reset_index()
            holdings = holdings.rename(
                columns={"Symbol": "Ticker", "Holding Percent": "Weight"}
            )

            if holdings["Weight"].sum() > 1:
                holdings["Weight"] = holdings["Weight"] / 100

            return holdings
    except Exception as e:
        logging.error(f"Error getting holdings: {str(e)}")
    return pd.DataFrame()


def is_fund(name):
    fund_keywords = ["ETF", "FUND", "TRUST", "AVANTIS", "VANGUARD", "ISHARES", "SPDR"]
    return any(keyword in str(name).upper() for keyword in fund_keywords)


def calculate_look_through(
    ticker, portfolio_weight=1.0, depth=0, processed_funds=None, max_depth=5
):
    if processed_funds is None:
        processed_funds = set()

    if depth > max_depth or ticker in processed_funds:
        logging.warning(f"Max depth reached or fund already processed: {ticker}")
        return pd.DataFrame()

    processed_funds.add(ticker)

    security = get_security_info(ticker)
    if security is None:
        return pd.DataFrame()

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

        if is_fund(row["Name"]):
            fund_ticker = row["Ticker"]
            logging.info(f"Found fund: {row['Name']} ({fund_ticker})")

            sleep(1)
            underlying_holdings = calculate_look_through(
                fund_ticker, weight, depth + 1, processed_funds
            )

            if not underlying_holdings.empty:
                final_holdings.append(underlying_holdings)
            else:
                final_holdings.append(
                    pd.DataFrame(
                        {
                            "Name": [row["Name"]],
                            "Ticker": [fund_ticker],
                            "Weight": [weight],
                            "Type": ["ETF"],
                            "Sector": ["ETF"],
                            "Nation": ["Unknown"],
                            "DirectHolding": [False],
                        }
                    )
                )
        else:
            stock_security = get_security_info(row["Ticker"])
            sector = get_sector(stock_security) if stock_security else "Unknown"
            nation = get_nation(stock_security) if stock_security else "Unknown"

            final_holdings.append(
                pd.DataFrame(
                    {
                        "Name": [row["Name"]],
                        "Ticker": [row["Ticker"]],
                        "Weight": [weight],
                        "Type": ["Stock"],
                        "Sector": [sector],
                        "Nation": [nation],
                        "DirectHolding": [False],
                    }
                )
            )

    return (
        pd.concat(final_holdings, ignore_index=True)
        if final_holdings
        else pd.DataFrame()
    )


def merge_holdings(combined):
    logging.info("Merging holdings...")
    combined["StandardTicker"] = combined["Ticker"].apply(standardize_ticker)

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
    merged["Name"] = merged.apply(
        lambda x: f"{x['Name']} *" if x["DirectHolding"] else x["Name"], axis=1
    )

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
