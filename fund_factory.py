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
        for holding_name, symbol, weight in data["holdings"]:
            scraper = Scraper(symbol, request_cache)
            holding_data = scraper.get_data()
            if holding_data["is_fund"]:
                holding = FundFactory.create(
                    holding_data, request_cache, weighting=weight
                )
            else:
                holding = StockFactory.create(holding_data, weighting=weight)
            fund._holdings.append(holding)
        return fund
