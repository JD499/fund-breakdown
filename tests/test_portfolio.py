import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from portfolio import Portfolio
from stock import Stock
from fund import Fund
import pytest


def test_add_holdings():
    """
    Test function to check if holdings can be added to a fund
    """
    portfolio = Portfolio()
    stock1 = Stock("AAPL", "Apple Inc.", 150.0, 100)
    stock2 = Stock("GOOG", "Alphabet Inc.", 200.0, 200)
    fund1 = Fund("SPY", "SPDR S&P 500 ETF Trust", 100.0, 300)
    portfolio.add_holding(stock1)
    portfolio.add_holding(stock2)
    portfolio.add_holding(fund1)
    assert portfolio.holdings[0] == stock2
    assert portfolio.holdings[1] == fund1
    assert portfolio.holdings[2] == stock1


def test_add_holding_with_invalid_type():
    """
    Test function to check if an error is raised when adding an invalid holding type
    """
    portfolio = Portfolio()
    with pytest.raises(TypeError):
        portfolio.add_holding("not a Stock or Fund object")


def holdings_table_string():
    """
    Test function to check if holdings table is generated correctly
    """
    portfolio = Portfolio()
    stock1 = Stock("AAPL", "Apple Inc.", 150.0, weighting=0.5)
    stock2 = Stock("AMZN", "Amazon.com, Inc.", 1000.0, weighting=0.3)
    stock3 = Stock("GOOG", "Alphabet Inc.", 1030.0, weighting=0.2)
    fund1 = Fund("FOO", "Foo Fund", 100.0, weighting=0.25)
    fund2 = Fund("BAR", "Bar Fund", 200.0, weighting=0.25)
    portfolio.add_holding(stock1)
    portfolio.add_holding(stock2)
    portfolio.add_holding(stock3)
    portfolio.add_holding(fund1)
    portfolio.add_holding(fund2)

    expected_output = "Holding              Weighting  Price     \n----------------------------------------\nApple Inc.           0.50       150.00    \nAmazon.com, Inc.     0.30       1000.00   \nFoo Fund             0.25       100.00    \nBar Fund             0.25       200.00    \nAlphabet Inc.        0.20       1030.00   \n"

    captured_output = portfolio.holdings_table_string()
    assert captured_output == expected_output


def test_calculate_portfolio_value():
    """
    Test function to check if the total value of a portfolio is calculated correctly
    """
    portfolio = Portfolio()
    stock1 = Stock("AAPL", "Apple Inc.", 150.0, shares=10)
    stock2 = Stock("AMZN", "Amazon.com, Inc.", 1000.0, shares=5)
    stock3 = Stock("GOOG", "Alphabet Inc.", 1030.0, shares=2)
    fund1 = Fund("FOO", "Foo Fund", 100.0, shares=20)
    fund2 = Fund("BAR", "Bar Fund", 200.0, shares=15)
    portfolio.add_holding(stock1)
    portfolio.add_holding(stock2)
    portfolio.add_holding(stock3)
    portfolio.add_holding(fund1)
    portfolio.add_holding(fund2)

    expected_output = 10 * 150.0 + 5 * 1000.0 + 2 * 1030.0 + 20 * 100.0 + 15 * 200.0
    assert portfolio.calculate_portfolio_value() == expected_output
