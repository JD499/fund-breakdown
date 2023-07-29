import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from stock import Stock

# Test for Stock class


def test_stock_init():
    stock = Stock("symbol")
    assert stock.symbol == "symbol"


def test_stock_properties():
    stock = Stock("symbol")
    stock.name = "name"
    stock.price = 100
    stock.shares = 10
    stock.weighting = 0.1
    assert stock.name == "name"
    assert stock.price == 100
    assert stock.shares == 10
    assert stock.weighting == 0.1


def test_stock_value():
    stock = Stock("symbol")
    stock.price = 100
    stock.shares = 10
    assert stock.value == 1000
