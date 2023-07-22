class Fund:
    def __init__(self, symbol, name, price, stocks=None, funds=None, weighting=None):
        self.symbol = symbol
        self.name = name
        self.price = price
        self.stocks = stocks or []
        self.funds = funds or []
        self._weighting = weighting
        
    def add_stock(self, stock):
        self.stocks.append(stock)

    def add_fund(self, fund):
        self.funds.append(fund)

    @property
    def weighting(self):
        return self._weighting

    @weighting.setter
    def weighting(self, value):
        self._weighting = value