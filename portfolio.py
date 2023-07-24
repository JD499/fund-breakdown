from stock import Stock
from fund import Fund


class Portfolio:
    """
    A class representing a portfolio of stocks and funds.

    Attributes:
    - stocks (list): A list of Stock objects representing the stocks in the portfolio.
    - funds (list): A list of Fund objects representing the funds in the portfolio.
    """

    def __init__(self, holdings=None):
        self.holdings = holdings or []

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

    def remove_holding(self, holding):
        """
        Removes a Stock or Fund object from the list of holdings that the fund contains.

        Args:
        holding (Stock or Fund): The Stock or Fund object to remove.
        """
        if not isinstance(holding, (Stock, Fund)):
            raise TypeError("Holding must be a Stock or Fund object")
        self.holdings.remove(holding)
        self.holdings.sort(key=lambda x: x.weighting, reverse=True)

    def holdings_table_string(self):
        """
        Returns a table of the fund's holdings as a string.

        Args:
            fund (self): The fund to return the holdings table for.

        Returns:
            str: A string representation of the holdings table.
        """
        table = ""
        table += f"{'Holding':<20} {'Weighting':<10} {'Price':<10}\n"
        table += "-" * 40 + "\n"
        for holding in self.holdings:
            table += f"{holding.name:<20} {holding.weighting:<10.2f} {holding.price:<10.2f}\n"
        return table
