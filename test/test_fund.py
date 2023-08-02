import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fund import Fund


# Test for Fund class


def test_fund_init():
    fund = Fund("symbol")
    assert fund.symbol == "symbol"


def test_fund_properties():
    fund = Fund("symbol")
    fund.name = "name"
    fund.price = 100
    fund.shares = 10
    fund.weighting = 0.1
    assert fund.name == "name"
    assert fund.price == 100
    assert fund.shares == 10
    assert fund.weighting == 0.1


def test_fund_value():
    fund = Fund("symbol")
    fund.price = 100
    fund.shares = 10
    assert fund.value == 1000


def test_fund_holdings():
    fund = Fund("symbol")
    fund2 = Fund("symbol2")
    fund.holdings = [fund2]
    assert fund.holdings == [fund2]


def test_fund_add_holding():
    fund = Fund("symbol")
    fund2 = Fund("symbol2")
    fund.add_holding(fund2)
    assert fund.holdings == [fund2]
