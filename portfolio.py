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

    def add_stock(self, stock):
        """
        Adds a stock to the portfolio.

        Args:
            stock (Stock): The stock to add.
        """
        self.stocks.append(stock)

    def remove_stock(self, stock):
        """
        Removes a stock from the portfolio.

        Args:
            stock (Stock): The stock to remove.
        """
        self.stocks.remove(stock)

    def add_fund(self, fund):
        """
        Adds a fund to the portfolio.

        Args:
            fund (Fund): The fund to add.
        """
        self.funds.append(fund)

    def remove_fund(self, fund):
        """
        Removes a fund from the portfolio.

        Args:
            fund (Fund): The fund to remove.
        """
        self.funds.remove(fund)
