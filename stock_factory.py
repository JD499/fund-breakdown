from stock import Stock


class StockFactory:
    @staticmethod
    def create(data, shares=None, weighting=None):
        stock = Stock(data['symbol'])
        stock._name = data['name']
        stock._price = data['price']
        stock._shares = shares
        stock._weighting = weighting
        return stock
