from stock import Stock


class Fund:
    def __init__(self, symbol):
        self._symbol = symbol
        self._name = ""
        self._price = 0
        self._shares = 0
        self._weighting = 0
        self._holdings = []
        self._value = 0

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def shares(self):
        return self._shares

    @shares.setter
    def shares(self, value):
        self._shares = value

    @property
    def weighting(self):
        return self._weighting

    @weighting.setter
    def weighting(self, value):
        self._weighting = value

    @property
    def value(self):
        if self._value != 0:  # If value has been manually set, return that
            return self._value
        else:  # If not, return price * shares
            return self._price * self._shares

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def holdings(self):
        return self._holdings

    @holdings.setter
    def holdings(self, value):
        if all(isinstance(i, (Stock, Fund)) for i in value):
            self._holdings = value
            self.set_holdings_values()
        else:
            raise ValueError("Holdings should be a list of Stock or Fund objects")

    def add_holding(self, holding):
        if isinstance(holding, (Stock, Fund)):
            self._holdings.append(holding)
            self.set_holdings_values()
        else:
            raise ValueError("Holding should be an instance of Stock or Fund")

    # approximate the value of each holding by dividing fund value by holding weight
    def set_holdings_values(self):
        """
        Sets the value of each holding in the fund.
        """
        total_value = self.value
        for holding in self.holdings:
            holding.value = total_value * holding.weighting

    def holdings_table_string(self):
        """
        Returns a table of the fund's holdings as a string.

        Args:
             (self): The fund to return the holdings table for.

        Returns:
            str: A string representation of the holdings table.
        """
        table = ""
        table += f"{'Holding':<20} {'Weighting':<10} {'Price':<10} {'Value':<10}\n"
        table += "-" * 50 + "\n"
        for holding in self.holdings:
            table += f"{holding.name:<20} {holding.weighting:<10.2f} {holding.price:<10.2f} {holding.value:<10.2f}\n"  # noqa: E501
        return table
