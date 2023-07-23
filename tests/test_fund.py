import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fund import Fund  # noqa: E402
from stock import Stock  # noqa: E402


def test_add_stock():
    """
    Test function to check if a stock can be added to a fund
    """
    fund = Fund("FOO", "Foo Fund", 100.0)
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    fund.add_stock(stock)
    assert len(fund.stocks) == 1
    assert fund.stocks[0] == stock


def test_add_fund():
    """
    Test function to check if a fund can be added to another fund
    """
    fund1 = Fund("FOO", "Foo Fund", 100.0)
    fund2 = Fund("BAR", "Bar Fund", 200.0)
    fund1.add_fund(fund2)
    assert len(fund1.funds) == 1
    assert fund1.funds[0] == fund2


def test_set_price():
    """
    Test function to check if the price of a fund can be set
    """
    fund = Fund("FOO", "Foo Fund", 100.0)
    fund.price = 200.0
    assert fund.price == 200.0


def test_set_price_with_non_float_value():
    """
    Test function to check if the price of a fund can be set with a non-float value
    """
    fund = Fund("FOO", "Foo Fund", 100.0)
    with pytest.raises(TypeError):
        fund.price = "not a float"


def test_set_weighting():
    """
    Test function to check if the weighting of a fund can be set
    """
    fund = Fund("FOO", "Foo Fund", 100.0)
    fund.weighting = 0.5
    assert fund.weighting == 0.5


def test_set_weighting_with_non_float_value():
    """
    Test function to check if the weighting of a fund can be set with a non-float value
    """
    fund = Fund("FOO", "Foo Fund", 100.0)
    with pytest.raises(TypeError):
        fund.weighting = "not a float"


def test_add_stock_and_fund():
    """
    Test function to check if a stock and a fund can be added to a fund
    """
    fund = Fund("FOO", "Foo Fund", 100.0)
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    fund1 = Fund("BAR", "Bar Fund", 200.0)
    fund.add_stock(stock)
    fund.add_fund(fund1)
    assert len(fund.stocks) == 1
    assert fund.stocks[0] == stock
    assert len(fund.funds) == 1
    assert fund.funds[0] == fund1
