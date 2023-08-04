import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import Scraper
from request_cache import RequestCache


def test_scraper_init():
    request_cache = RequestCache()
    scraper = Scraper("symbol", request_cache)
    assert scraper._symbol == "symbol"


def test_scraper_is_fund():
    request_cache = RequestCache()

    scraper = Scraper("AAPL", request_cache)
    assert scraper.is_fund() == False


def test_scraper_get_price():
    request_cache = RequestCache()

    scraper = Scraper("AAPL", request_cache)
    assert isinstance(scraper.get_price(), float)


def test_scraper_get_name():
    request_cache = RequestCache()

    scraper = Scraper("AAPL", request_cache)
    assert scraper.get_name() == "Apple Inc."


def test_scraper_get_holdings():
    request_cache = RequestCache()

    scraper = Scraper("AAPL", request_cache)
    assert scraper.get_holdings() is None


def test_scraper_get_data():
    request_cache = RequestCache()

    scraper = Scraper("AAPL", request_cache)
    data = scraper.get_data()

    assert data["symbol"] == "AAPL"
    assert data["name"] == "Apple Inc."
    assert isinstance(data["price"], float)
    assert data["holdings"] is None
    assert data["is_fund"] == False
