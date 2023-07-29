import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from portfolio import Portfolio
from fund import Fund
from stock import Stock

# Test for Portfolio class


def test_portfolio_init():
    portfolio = Portfolio()
    assert portfolio.holdings == []


def test_portfolio_holdings():
    portfolio = Portfolio()
    fund = Fund("symbol")
    portfolio.holdings = [fund]
    assert portfolio.holdings == [fund]


def test_portfolio_value():
    portfolio = Portfolio()
    fund = Fund("symbol")
    fund.price = 100
    fund.shares = 10
    portfolio.holdings = [fund]
    assert portfolio.value == 1000


def test_portfolio_add_holding():
    portfolio = Portfolio()
    fund = Fund("symbol")
    fund.shares = 10
    fund.price = 100
    portfolio.add_holding(fund)
    assert portfolio.holdings == [fund]
