class Fund:
    def __init__(self, symbol, name, price, stocks=None, funds=None, weighting=None):
        """
        Initializes a Fund object with the given parameters.

        Args:
        symbol (str): The symbol of the fund.
        name (str): The name of the fund.
        price (float): The price of the fund.
        stocks (list, optional): A list of Stock objects that the fund contains. 
        funds (list, optional): A list of Fund objects that the fund contains. 
        weighting (float, optional): The weighting of the fund. 
        """
        self.symbol = symbol
        self.name = name
        self.price = price
        self.stocks = stocks or []
        self.funds = funds or []
        self._weighting = weighting

    def add_stock(self, stock):
        """
        Adds a Stock object to the list of stocks that the fund contains.

        Args:
        stock (Stock): The Stock object to add.
        """
        self.stocks.append(stock)

    def add_fund(self, fund):
        """
        Adds a Fund object to the list of funds that the fund contains.

        Args:
        fund (Fund): The Fund object to add.
        """
        self.funds.append(fund)

    @property
    def weighting(self):
        """
        Returns the weighting of the fund.
        """
        return self._weighting

    @weighting.setter
    def weighting(self, value):
        """
        Sets the weighting of the fund to the given value.

        Args:
        value (float): The new weighting value.
        """
        self._weighting = value
