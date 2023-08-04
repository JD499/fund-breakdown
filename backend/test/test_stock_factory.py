import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_factory import StockFactory


# Test for StockFactory class


def test_stock_factory_create():
    data = {"symbol": "symbol", "name": "name", "price": 100}
    stock = StockFactory.create(data)
    assert stock.symbol == "symbol"
    assert stock.name == "name"
    assert stock.price == 100
