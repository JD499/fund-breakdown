from stock import Stock
from fund import Fund


class Portfolio:
    def __init__(self, holdings=None):
        self._holdings = holdings or []

    @property
    def holdings(self):
        return self._holdings

    @holdings.setter
    def holdings(self, value):
        if all(isinstance(i, (Stock, Fund)) for i in value):
            self._holdings = value
        else:
            raise ValueError("Holdings should be a list of Stock or Fund objects")

    @property
    def value(self):
        return sum(holding.value for holding in self._holdings)

    def add_holding(self, holding):
        if isinstance(holding, (Stock, Fund)):
            self._holdings.append(holding)
            self.set_holdings_weights()
        else:
            raise ValueError("Holding should be an instance of Stock or Fund")

    def set_holdings_weights(self):
        """
        Sets the weighting of each holding in the portfolio.
        """
        total_value = sum(holding.value for holding in self.holdings)
        for holding in self.holdings:
            holding.weighting = holding.value / total_value

    def holdings_table_string(self):
        """
        Returns a table of the fund's holdings as a string.

        Args:
            fund (self): The fund to return the holdings table for.

        Returns:
            str: A string representation of the holdings table.
        """
        table = ""
        table += f"{'Holding':<20} {'Weighting':<10} {'Price':<10} {'Value':<10}\n"
        table += "-" * 50 + "\n"
        for holding in self.holdings:
            table += f"{holding.name:<20} {holding.weighting:<10.2f} {holding.price:<10.2f} {holding.value:<10.2f}\n"  # noqa: E501
        return table
