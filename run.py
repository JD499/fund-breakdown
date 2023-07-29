from portfolio import Portfolio
from scraper import Scraper
from request_cache import RequestCache
from fund_factory import FundFactory
from stock_factory import StockFactory

def main():
    portfolio = Portfolio()
    request_cache = RequestCache()


    for i in range(2):
        symbol = input(f"Enter the symbol for holding {i+1}: ")

        scraper = Scraper(symbol, request_cache)
        data = scraper.get_data()

        shares = int(input(f"Enter the number of shares for {symbol}: "))

        if data["is_fund"]:
            fund = FundFactory.create(data,request_cache)
            fund.shares = shares

            # Assuming set_holdings_values method is in Fund class
            fund.set_holdings_values()

            print(fund.holdings_table_string())

            for holding in fund.holdings:
                portfolio.add_holding(holding)

        else:
            stock = StockFactory.create(data)
            stock.shares = shares
            portfolio.add_holding(stock)

    print("The holdings in your portfolio are:")
    print(portfolio.holdings_table_string())

if __name__ == "__main__":
    main()
