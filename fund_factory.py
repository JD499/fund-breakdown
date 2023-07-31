from fund import Fund
from scraper import Scraper
from stock_factory import StockFactory


class FundFactory:
    @staticmethod
    def create(data, request_cache, shares=None, weighting=None):
        fund = Fund(data["symbol"])
        fund._name = data["name"]
        fund._price = data["price"]
        fund._shares = shares
        fund._weighting = weighting
        fund._holdings = []

        # Get the symbols for all holdings
        symbols = [symbol for _, symbol, _ in data["holdings"]]

        if symbols:  # Check if the symbols list is not empty
            # Create a Scraper and use get_multiple_data to fetch data for all holdings
            scraper = Scraper(symbols[0], request_cache)
            data_list = scraper.get_multiple_data(symbols)

            # Create a dictionary that maps symbols to data
            data_dict = {
                holding_data["symbol"]: holding_data for holding_data in data_list
            }

            for holding_name, symbol, weight in data["holdings"]:
                holding_data = data_dict[symbol]
                if holding_data["is_fund"]:
                    holding = FundFactory.create(
                        holding_data, request_cache, weighting=weight
                    )
                else:
                    holding = StockFactory.create(holding_data, weighting=weight)
                fund._holdings.append(holding)
        return fund
