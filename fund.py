from stock import Stock


class Fund:
    def __init__(self, symbol, name, price, holdings=None, weighting=None):
        """
        Initializes a Fund object with the given parameters.

        Args:
        symbol (str): The symbol of the fund.
        name (str): The name of the fund.
        price (float): The price of the fund.
        holdings (list, optional): A list of Stock and Fund objects that the fund contains.
        weighting (float, optional): The weighting of the fund.
        """  # noqa: E501
        self.symbol = symbol
        self.name = name
        self.price = price
        self.holdings = holdings or []
        self._weighting = weighting

    def add_holding(self, holding):
        """
        Adds a Stock or Fund object to the list of holdings that the fund contains.

        Args:
        holding (Stock or Fund): The Stock or Fund object to add.
        """
        if not isinstance(holding, (Stock, Fund)):
            raise TypeError("Holding must be a Stock or Fund object")
        if not hasattr(holding, "weighting"):
            raise AttributeError("Holding must have a weighting attribute")
        if not isinstance(holding.weighting, float):
            raise TypeError("Holding weighting must be a float")
        self.holdings.append(holding)
        self.holdings.sort(key=lambda x: x.weighting, reverse=True)

    @property
    def price(self):
        """
        Gets the current price of the stock.

        Returns:
            float: The current price of the stock.
        """
        return self._price

    @price.setter
    def price(self, value):
        """
        Sets the current price of the stock.

        Args:
            value (float): The new price of the stock.
        """
        if not isinstance(value, float):
            raise TypeError("Price must be a float")
        self._price = value

    @property
    def weighting(self):
        """
        Gets the weighting of the stock in a portfolio.

        Returns:
            float: The weighting of the stock in a portfolio.
        """
        return self._weighting

    @weighting.setter
    def weighting(self, value):
        """
        Sets the weighting of the stock in a portfolio.

        Args:
            value (float): The new weighting of the stock in a portfolio.
        """
        if value is not None and not isinstance(value, float):
            raise TypeError("Weighting must be a float or None")
        self._weighting = value
