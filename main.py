from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import yfinance as yf
import pandas as pd
from time import sleep
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("portfolio_analyzer.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

TICKER_MAPPINGS = {
    "SMSN": "SMSN.IL",
    "00939": "0939.HK",
    "RIGD": "RIGD.IL",
}


def remap_ticker(ticker):
    mapped_ticker = TICKER_MAPPINGS.get(ticker, ticker)
    if mapped_ticker != ticker:
        logger.info(f"Remapped ticker {ticker} to {mapped_ticker}")
    return mapped_ticker


def get_security_info(ticker):
    try:
        ticker = remap_ticker(ticker)

        logger.info(f"Fetching data for {ticker}...")
        security = yf.Ticker(ticker)

        if not hasattr(security, "info") or security.info is None:
            logger.error(f"Could not fetch info for {ticker}")
            raise ValueError(f"Could not fetch info for {ticker}")

        try:
            fast_info = security.fast_info
            if fast_info is None:
                logger.error(f"{ticker} has no fast_info data")
                raise ValueError(f"Could not fetch price data for {ticker}")
        except Exception as e:
            logger.error(f"Error getting fast_info for {ticker}: {str(e)}")
            raise ValueError(f"Could not fetch price data for {ticker}")

        try:
            if pd.isna(fast_info["lastPrice"]) or fast_info["lastPrice"] == 0:
                logger.error(f"{ticker} has no valid price data")
                raise ValueError(f"No valid price data for {ticker}")
        except (KeyError, AttributeError):
            logger.error(f"Could not verify price data for {ticker}")
            raise ValueError(f"Could not verify price data for {ticker}")

        return security

    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        raise ValueError(f"Failed to process {ticker}: {str(e)}")


def get_sector(security):
    try:
        sector = security.info.get("sector", "")
        if not sector or pd.isna(sector):
            sector = security.info.get("industry", "Unknown")
        if not sector or pd.isna(sector):
            logger.warning(f"No sector information found for security")
            return "Unknown"
        return sector
    except:
        logger.warning(f"Error getting sector information")
        return "Unknown"


def get_nation(security):
    try:
        country = security.info.get("country", "")

        if not country or pd.isna(country):
            return "Unknown"

        return country
    except:
        logger.warning(f"Error getting country information")
        return "Unknown"


def get_etf_sector_breakdown(security):
    try:
        if hasattr(security, "funds_data"):
            sector_data = security.funds_data.sector_weightings
            if sector_data is not None:
                return {k.capitalize(): v for k, v in sector_data.items()}
    except:
        logger.warning(f"Error getting ETF sector breakdown")
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
        logger.warning(f"Error determining if security is ETF")
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
        logger.error(f"Error getting holdings: {str(e)}")
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
        logger.warning(f"Max depth reached or fund already processed: {ticker}")
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
        logger.info(
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
        logger.warning(f"No holdings data available for {ticker}")
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
    logger.info(
        f"Processing {ticker} ({portfolio_weight:.1f}% of portfolio) with {len(holdings)} holdings..."
    )

    for _, row in holdings.iterrows():
        weight = row["Weight"] * portfolio_weight

        if is_fund(row["Name"]):
            fund_ticker = row["Ticker"]
            logger.info(f"Found fund: {row['Name']} ({fund_ticker})")

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
    logger.info("Merging holdings...")
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
    logger.info("Calculating sector breakdown...")
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


def get_portfolio_input():
    logger.info("Getting portfolio input...")
    portfolio = {}

    while True:
        try:
            line = input("> ").strip()
            if not line:
                break

            parts = line.split()
            if len(parts) != 2:
                logger.warning("Invalid input format")
                continue

            ticker, weight = parts
            weight = float(weight)

            if weight <= 0:
                logger.warning("Invalid weight (non-positive)")
                continue

            portfolio[ticker.upper()] = weight / 100

        except ValueError:
            logger.warning("Invalid weight format")
            continue

    total_weight = sum(portfolio.values())
    if total_weight == 0:
        logger.warning("Empty portfolio")
        return {}

    return {ticker: weight / total_weight for ticker, weight in portfolio.items()}


def analyze_portfolio():
    logger.info("Starting portfolio analysis...")
    portfolio = get_portfolio_input()
    if not portfolio:
        logger.warning("No valid portfolio entered")
        return

    for ticker, weight in portfolio.items():
        security = get_security_info(ticker)
        if security:
            pass

    all_holdings = []
    for ticker, weight in portfolio.items():
        holdings = calculate_look_through(ticker, weight)
        if not holdings.empty:
            all_holdings.append(holdings)

    if not all_holdings:
        logger.warning("No holdings data available")
        return

    combined = pd.concat(all_holdings, ignore_index=True)
    merged = merge_holdings(combined)

    logger.info("Generating results...")
    display_df = merged.head(50).copy()
    display_df.index = range(1, len(display_df) + 1)
    display_df["Weight"] = display_df["Weight"] * 100

    pd.set_option("display.max_rows", None)


def validate_portfolio_weights(portfolio):
    if not portfolio:
        return False, "Portfolio is empty"

    total_weight = sum(weight for weight in portfolio.values())

    if abs(total_weight - 100) > 0.01:
        logger.warning(f"Portfolio weights sum to {total_weight}%, not 100%")
        return (
            False,
            f"Portfolio weights must sum to 100% (currently {total_weight:.2f}%)",
        )

    for ticker, weight in portfolio.items():
        if weight <= 0:
            logger.warning(f"Invalid weight for {ticker}: {weight}%")
            return False, f"Invalid weight for {ticker}: {weight}% (must be positive)"
        if weight > 100:
            logger.warning(f"Invalid weight for {ticker}: {weight}%")
            return False, f"Invalid weight for {ticker}: {weight}% (must be ≤ 100%)"

    logger.info("Portfolio weights validated successfully")
    return True, ""


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("Serving home page")
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze(request: Request):
    logger.info("Processing analysis request")
    form_data = await request.form()
    portfolio = {}
    for key, value in form_data.items():
        if key.startswith("ticker_"):
            ticker = value.strip().upper()
            weight = float(form_data.get(f"weight_{key[7:]}", 0))
            if ticker and weight > 0:
                portfolio[ticker] = weight

    is_valid, error_message = validate_portfolio_weights(portfolio)
    if not is_valid:
        logger.warning(f"Portfolio validation failed: {error_message}")
        return {"error": error_message}

    all_holdings = []
    for ticker, weight in portfolio.items():
        holdings = calculate_look_through(ticker, weight)
        if not holdings.empty:
            all_holdings.append(holdings)

    if not all_holdings:
        logger.warning("No holdings data available")
        return {"error": "No holdings data available"}

    combined = pd.concat(all_holdings, ignore_index=True)
    merged = merge_holdings(combined)
    holdings_data = merged.head(50).to_dict(orient="records")

    sector_breakdown = calculate_portfolio_sector_breakdown(portfolio)

    logger.info("Analysis complete")
    return {"holdings": holdings_data, "sectors": sector_breakdown}
