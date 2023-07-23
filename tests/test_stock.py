import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from stock import Stock


def test_create_stock():
    """
    Test creating a Stock object with symbol, name, and price.
    """
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    assert stock.symbol == "AAPL"
    assert stock.name == "Apple Inc."
    assert stock.price == 135.39
    assert stock.weighting is None

def test_set_price():
    """
    Test setting the price of a Stock object.
    """
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    stock.price = 140.00
    assert stock.price == 140.00

def test_set_weighting():
    """
    Test setting the weighting of a Stock object.
    """
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    stock.weighting = 0.25
    assert stock.weighting == 0.25

def test_set_price_with_non_float_value():
    """
    Test setting the price of a Stock object with a non-float value.
    """
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    with pytest.raises(TypeError):
        stock.price = "invalid"

def test_set_weighting_with_non_float_value():
    """
    Test setting the weighting of a Stock object with a non-float value.
    """
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    with pytest.raises(TypeError):
        stock.weighting = "invalid"

def test_set_symbol():
    """
    Test setting the symbol of a Stock object.
    """
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    with pytest.raises(AttributeError):
        stock.symbol = "GOOG" # type: ignore

def test_set_name():
    """
    Test setting the name of a Stock object.
    """
    stock = Stock("AAPL", "Apple Inc.", 135.39)
    with pytest.raises(AttributeError):
        stock.name = "Google Inc." # type: ignore
