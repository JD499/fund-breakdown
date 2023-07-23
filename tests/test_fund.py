import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fund import Fund  # noqa: E402
from stock import Stock  # noqa: E402


def test_add_holding():
    """
    Test function to check if a stock and a fund can be added to a fund
    """
    fund = Fund("FOO", "Foo Fund", 100.0)
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    fund1 = Fund("BAR", "Bar Fund", 200.0)
    fund.add_holding(stock)
    fund.add_holding(fund1)
    assert len(fund.holdings) == 2
    assert fund.holdings[0] == stock
    assert fund.holdings[1] == fund1


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


def test_add_holding_with_invalid_type():
    """
    Test function to check if an error is raised when adding an invalid holding type
    """
    fund = Fund("FOO", "Foo Fund", 100.0)
    with pytest.raises(TypeError):
        fund.add_holding("not a Stock or Fund object")
