import sys
import os

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
    Test that the get_holdings method of the Scraper class returns a list of tuples,
    where each tuple contains
    a stock symbol, a company name, and a float greater than 0.0 representing the
    percentage of holdings for that stock.
    """
    scraper = Scraper("SPY")
    holdings = scraper.get_holdings()
    assert isinstance(holdings, list)
    assert len(holdings) > 0
    for holding in holdings:
        assert isinstance(holding, tuple)
        assert len(holding) == 3
        assert isinstance(holding[0], str)
        assert isinstance(holding[1], str)
        assert isinstance(holding[2], float)
        assert holding[2] > 0.0


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
