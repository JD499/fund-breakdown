class Stock:
    def __init__(self, symbol, name, price, shares=None, weighting=None):
        """
        Initializes a new instance of the Stock class.

        Args:
            symbol (str): The stock symbol.
            name (str): The name of the stock.
            price (float): The current price of the stock.
            weighting (float, optional): The weighting of the stock in a portfolio.
        """
        self._symbol = symbol
        self._name = name
        self._price = price
        self.shares = shares or 0
        self._weighting = weighting

    @property
    def symbol(self):
        """
        Gets the stock symbol.

        Returns:
            str: The stock symbol.
        """
        return self._symbol

    @property
    def name(self):
        """
        Gets the name of the stock.

        Returns:
            str: The name of the stock.
        """
        return self._name

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
