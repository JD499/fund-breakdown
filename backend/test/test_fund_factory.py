import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fund_factory import FundFactory
from request_cache import RequestCache


# Test for FundFactory class


def test_fund_factory_create():
    data = {"symbol": "symbol", "name": "name", "price": 100, "holdings": []}
    request_cache = RequestCache()
    fund = FundFactory.create(data, request_cache)
    assert fund.symbol == "symbol"
    assert fund.name == "name"
    assert fund.price == 100
