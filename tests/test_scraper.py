import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scraper import Scraper

def test_get_name():
    scraper = Scraper("AAPL")
    name = scraper.get_name()
    assert name == "Apple Inc. (AAPL)"

def test_get_holdings():
    scraper = Scraper("SPY")
    holdings = scraper.get_holdings()
    assert isinstance(holdings, dict)
    assert len(holdings) > 0
    for _, info in holdings.items():
        assert isinstance(info, dict)
        assert "name" in info
        assert "weight" in info
        assert isinstance(info["name"], str)
        assert isinstance(info["weight"], float)

def test_get_holdings_invalid_symbol():
    scraper = Scraper("INVALID_SYMBOL")
    holdings = scraper.get_holdings()
    assert holdings is None

def test_get_holdings_no_table():
    scraper = Scraper("GOOG")
    holdings = scraper.get_holdings()
    assert holdings is None