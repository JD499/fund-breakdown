import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import Scraper
from request_cache import RequestCache


# Test for Scraper class


def test_scraper_init():
    request_cache = RequestCache()
    scraper = Scraper("symbol", request_cache)
    assert scraper._symbol == "symbol"


# Note: The following tests are commented out because they make real HTTP requests.
# Uncomment them to run the tests, but be aware that they may fail if the website layout changes or if there are network issues.


def test_scraper_is_fund():
    request_cache = RequestCache()
    # noinspection SpellCheckingInspection
    scraper = Scraper("AAPL", request_cache)
    assert scraper.is_fund() == False


def test_scraper_get_price():
    request_cache = RequestCache()
    # noinspection SpellCheckingInspection
    scraper = Scraper("AAPL", request_cache)
    assert isinstance(scraper.get_price(), float)


def test_scraper_get_name():
    request_cache = RequestCache()
    # noinspection SpellCheckingInspection
    scraper = Scraper("AAPL", request_cache)
    assert scraper.get_name() == "Apple Inc."


def test_scraper_get_holdings():
    request_cache = RequestCache()
    # noinspection SpellCheckingInspection
    scraper = Scraper("AAPL", request_cache)
    assert scraper.get_holdings() is None


def test_scraper_get_data():
    request_cache = RequestCache()
    # noinspection SpellCheckingInspection
    scraper = Scraper("AAPL", request_cache)
    data = scraper.get_data()
    # noinspection SpellCheckingInspection
    assert data["symbol"] == "AAPL"
    assert data["name"] == "Apple Inc."
    assert isinstance(data["price"], float)
    assert data["holdings"] is None
    assert data["is_fund"] == False
