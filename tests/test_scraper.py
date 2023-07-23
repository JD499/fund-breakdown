import sys
import os
from fund import Fund
from stock import Stock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scraper import Scraper  # noqa: E402


def test_get_price():
    """
    Test that the get_price method of the Scraper class returns a float greater than 0.0
    for a valid stock symbol.
    """
    scraper = Scraper("AAPL")
    price = scraper.get_price()
    assert isinstance(price, float)
    assert price > 0.0


def test_get_invalid_price():
    """
    Test that the get_price method of the Scraper class raises a ValueError for
    an invalid stock symbol.
    """
    scraper = Scraper("INVALID")
    try:
        price = scraper.get_price()
    except ValueError:
        price = None
    assert price is None


def test_get_name():
    """
    Test that the get_name method of the Scraper class returns a non-empty string for a
    valid stock symbol.
    """
    scraper = Scraper("AAPL")
    name = scraper.get_name()
    assert isinstance(name, str)
    assert len(name) > 0


def test_get_invalid_name():
    """
    Test that the get_name method of the Scraper class raises a ValueError for an
    invalid stock symbol.
    """
    scraper = Scraper("INVALID")
    try:
        name = scraper.get_name()
    except ValueError:
        name = None
    assert name is None


def test_get_holdings():
    """
    Test that the get_holdings method of the Scraper class returns a list of Fund or Stock objects
    representing the holdings of a fund.
    """
    scraper = Scraper("SPY")
    holdings = scraper.get_holdings()
    assert isinstance(holdings, list)
    assert all(isinstance(holding, (Fund, Stock)) for holding in holdings)
    assert all(holding.symbol is not None for holding in holdings)
    assert all(holding.name is not None for holding in holdings)
    assert all(holding.price is not None for holding in holdings)
    assert all(holding.weighting is not None for holding in holdings)


def test_get_holdings_invalid():
    """
    Test that the get_holdings method of the Scraper class returns None for an invalid
    stock symbol.
    """
    scraper = Scraper("INVALID")
    holdings = scraper.get_holdings()
    assert holdings is None


def test_get_holdings_no_table():
    """
    Test that the get_holdings method of the Scraper class returns None when there is
    no holdings table available
    for a valid stock symbol.
    """
    scraper = Scraper("AAPL")
    holdings = scraper.get_holdings()
    assert holdings is None


def test_is_fund_true():
    """
    Test that the is_fund method of the Scraper class returns True for a fund symbol.
    """
    scraper = Scraper("SPY")
    assert scraper.is_fund() is True


def test_is_fund_false():
    """
    Test that the is_fund method of the Scraper class returns False for
    a non-fund symbol.
    """
    scraper = Scraper("AAPL")
    assert scraper.is_fund() is False
