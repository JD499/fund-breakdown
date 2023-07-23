import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from portfolio import Portfolio
from stock import Stock
from fund import Fund


def test_add_stock():
    """
    Test function to check if a stock can be added to the portfolio
    """
    portfolio = Portfolio()
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    portfolio.add_stock(stock)
    assert len(portfolio.stocks) == 1
    assert portfolio.stocks[0] == stock


def test_add_fund():
    """
    Test function to check if a fund can be added to the portfolio
    """
    portfolio = Portfolio()
    fund = Fund("FOO", "Foo Fund", 100.0)
    portfolio.add_fund(fund)
    assert len(portfolio.funds) == 1
    assert portfolio.funds[0] == fund


def test_remove_stock():
    """
    Test function to check if a stock can be removed from the portfolio
    """
    portfolio = Portfolio()
    stock1 = Stock("AAPL", "Apple Inc.", 135.39)
    stock2 = Stock("MSFT", "Microsoft Corporation", 231.60)
    portfolio.add_stock(stock1)
    portfolio.add_stock(stock2)
    portfolio.remove_stock(stock1)
    assert len(portfolio.stocks) == 1
    assert portfolio.stocks[0] == stock2


def test_remove_fund():
    """
    Test function to check if a fund can be removed from the portfolio
    """
    portfolio = Portfolio()
    fund1 = Fund("FOO", "Foo Fund", 100.0)
    fund2 = Fund("BAR", "Bar Fund", 200.0)
    portfolio.add_fund(fund1)
    portfolio.add_fund(fund2)
    portfolio.remove_fund(fund1)
    assert len(portfolio.funds) == 1
    assert portfolio.funds[0] == fund2
