from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup

from constants import BASE_URL, SYMBOL_CORRECTIONS
from utilities import remove_symbol


class Scraper:
    def __init__(self, symbol, request_cache):
        self._symbol = SYMBOL_CORRECTIONS.get(symbol, symbol)
        self._request_cache = request_cache
        self._is_fund = None

    def _get_url(self, endpoint=""):
        return f"{BASE_URL}{self._symbol}{endpoint}"

    def _make_request(self, url):
        return self._request_cache.get(url)

    def _get_soup(self, url):
        response = self._make_request(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def is_fund(self):
        url = self._get_url("/holdings?p=" + self._symbol)
        soup = self._get_soup(url)
        table = soup.find("table", {"class": "W(100%) M(0) BdB Bdc($seperatorColor)"})
        self._is_fund = table is not None
        return self._is_fund

    def get_price(self):
        url = self._get_url()
        soup = self._get_soup(url)
        price_element = soup.find(
            "fin-streamer", {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"}
        )
        if price_element is None:
            raise ValueError("Unable to find price element on page")
        price = price_element["value"]  # type: ignore
        return float(price)  # type: ignore

    def get_name(self):
        url = self._get_url()
        soup = self._get_soup(url)
        name_element = soup.find("h1", {"class": "D(ib) Fz(18px)"})
        if name_element is None:
            new_symbol = input(
                f"Unable to find name element on page for {self._symbol}. Please enter a new symbol: "  # noqa: E501
            )
            self._symbol = new_symbol
            return self.get_name()
        name = name_element.text
        name = remove_symbol(name)
        return name

    def get_holdings(self):
        if not self.is_fund():
            return None

        url = self._get_url("/holdings?p=" + self._symbol)
        soup = self._get_soup(url)

        table = soup.find("table", {"class": "W(100%) M(0) BdB Bdc($seperatorColor)"})

        rows = table.find_all("tr")[1:]  # type: ignore

        holdings = []
        for row in rows:
            cols = row.find_all("td")
            cols = [col.text.strip() for col in cols]
            holding_name, symbol, weight = cols[0], cols[1], cols[2]

            symbol = SYMBOL_CORRECTIONS.get(symbol, symbol)

            weight = float(weight[:-1]) / 100
            holding_name = remove_symbol(holding_name)

            holdings.append((holding_name, symbol, weight))

        if len(holdings) == 0:
            return None
        else:
            return holdings

    def get_data(self):
        data = {
            "symbol": self._symbol,
            "name": self.get_name(),
            "price": self.get_price(),
            "holdings": self.get_holdings() if self.is_fund() else None,
            "is_fund": self.is_fund(),
        }
        return data

    def get_data_for_symbol(self, symbol):
        scraper = Scraper(symbol, self._request_cache)
        return scraper.get_data()

    def get_multiple_data(self, symbols):
        with ThreadPoolExecutor() as executor:
            return list(executor.map(self.get_data_for_symbol, symbols))
