class Portfolio:
    """
    A class representing a portfolio of stocks and funds.

    Attributes:
    - stocks (list): A list of Stock objects representing the stocks in the portfolio.
    - funds (list): A list of Fund objects representing the funds in the portfolio.
    """

    def __init__(self, stocks=None, funds=None):
        self.stocks = stocks or []
        self.funds = funds or []
