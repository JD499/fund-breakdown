import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


def test_add_holding():
    portfolio = Portfolio()
    # noinspection SpellCheckingInspection
    apple_stock_1 = Stock('AAPL')
    apple_stock_1.value = 1000
    # noinspection SpellCheckingInspection
    apple_stock_2 = Stock('AAPL')
    apple_stock_2.value = 2000

    portfolio.add_holding(apple_stock_1)
    portfolio.add_holding(apple_stock_2)

    assert len(portfolio.holdings) == 1
    assert portfolio.holdings[0].value == 3000


def test_add_holding_different_stocks():
    portfolio = Portfolio()
    # noinspection SpellCheckingInspection
    apple_stock = Stock('AAPL')
    apple_stock.value = 1000
    google_stock = Stock('GOOGL')
    google_stock.value = 2000

    portfolio.add_holding(apple_stock)
    portfolio.add_holding(google_stock)

    assert len(portfolio.holdings) == 2
    assert portfolio.holdings[0].value == 1000
    assert portfolio.holdings[1].value == 2000
