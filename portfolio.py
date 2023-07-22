class Portfolio:
    def __init__(self, stocks=None, funds=None):
        self.stocks = stocks or []
        self.funds = funds or []