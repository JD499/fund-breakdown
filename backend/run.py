from concurrent.futures import ThreadPoolExecutor

from fund import Fund
from fund_factory import FundFactory
from portfolio import Portfolio
from request_cache import RequestCache
from scraper import Scraper
from stock_factory import StockFactory


def process_holding(holding, request_cache, portfolio):
    if isinstance(holding, Fund):
        holding.set_holdings_values()
        print(holding.holdings_table_string())
        with ThreadPoolExecutor() as executor:
            executor.map(lambda sub_holding: process_holding(sub_holding, request_cache, portfolio), holding.holdings)
    else:
        portfolio.add_holding(holding)


def main():
    portfolio = Portfolio()
    request_cache = RequestCache()

    symbols = [input(f"Enter the symbol for holding {i + 1}: ") for i in range(2)]
    with ThreadPoolExecutor() as executor:
        data_list = list(executor.map(lambda symbol: Scraper(symbol, request_cache).get_data(), symbols))

    for data in data_list:
        shares = int(input(f"Enter the number of shares for {data['symbol']}: "))

        if data["is_fund"]:
            fund = FundFactory.create(data, request_cache)
            fund.shares = shares

            process_holding(fund, request_cache, portfolio)
        else:
            stock = StockFactory.create(data)
            stock.shares = shares
            portfolio.add_holding(stock)

    print("The holdings in your portfolio are:")
    print(portfolio.holdings_table_string())


if __name__ == "__main__":
    main()
