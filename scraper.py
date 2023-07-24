import requests
from fund import Fund
from stock import Stock
from bs4 import BeautifulSoup
from utilities import remove_symbol


class Scraper:
    def __init__(self, symbol):
        """
        Initializes a new instance of the Scraper class with the specified symbol.

        Args:
            symbol (str): The symbol of the fund to scrape.
        """
        self._symbol = symbol
        self._cache = {}

    def _make_request(self, url):
        """
        Sends an HTTP GET request to the specified URL and returns the response.

        Args:
            url (str): The URL to send the request to.

        Returns:
            requests.Response: The response to the request.
        """
        if url in self._cache:
            return self._cache[url]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        self._cache[url] = response
        return response

    def _get_soup(self, url):
        """
        Sends an HTTP GET request to the specified URL, retrieves the HTML content, and
        returns a BeautifulSoup object.

        Args:
            url (str): The URL to retrieve the HTML content from.

        Returns:
            bs4.BeautifulSoup: A BeautifulSoup object representing the HTML content
            of the page.
        """
        response = self._make_request(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def is_fund(self):
        """
        Checks if the symbol is a fund.

        Returns:
            bool: True if the symbol is a fund, False otherwise.
        """
        url = (
            f"https://finance.yahoo.com/quote/{self._symbol}/holdings?p={self._symbol}"
        )
        soup = self._get_soup(url)
        table = soup.find("table", {"class": "W(100%) M(0) BdB Bdc($seperatorColor)"})
        return table is not None

    def get_price(self):
        """
        Retrieves the current price of the stock or fund.

        Returns:
            float: The current price of the stock or fund.
        """
        url = f"https://finance.yahoo.com/quote/{self._symbol}"
        soup = self._get_soup(url)
        price_element = soup.find(
            "fin-streamer", {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"}
        )
        if price_element is None:
            raise ValueError("Unable to find price element on page")
        price = price_element["value"]  # type: ignore
        return float(price)  # type: ignore

    def get_name(self):
        """
        Retrieves the name of the stock or fund.

        Returns:
            str: The name of the stock or fund.
        """
        url = f"https://finance.yahoo.com/quote/{self._symbol}"
        soup = self._get_soup(url)
        name_element = soup.find("h1", {"class": "D(ib) Fz(18px)"})
        if name_element is None:
            raise ValueError("Unable to find name element on page")
        name = name_element.text
        name = remove_symbol(name)
        return name

    def get_holdings(self):
        """
        Retrieves the holdings of a fund.

        Returns:
            list: A list of Fund or Stock objects representing the holdings of the fund.
                  Returns None if the symbol is not a fund or if no holdings are found.
        """
        if not self.is_fund():
            return None

        url = (
            f"https://finance.yahoo.com/quote/{self._symbol}/holdings?p={self._symbol}"
        )
        soup = self._get_soup(url)

        table = soup.find("table", {"class": "W(100%) M(0) BdB Bdc($seperatorColor)"})

        rows = table.find_all("tr")[1:]  # type: ignore

        holdings = []
        for row in rows:
            cols = row.find_all("td")
            cols = [col.text.strip() for col in cols]
            holding_name, symbol, weight = cols[0], cols[1], cols[2]

            if symbol == "BRK.B":
                symbol = "BRK-B"
            elif symbol == "BRK.A":
                symbol = "BRK-A"
            weight = float(weight[:-1])
            holding_name = remove_symbol(holding_name)

            # check if holding is stock or fund
            holding_scraper = Scraper(symbol)
            if holding_scraper.is_fund():
                holding = Fund(
                    symbol, holding_name, holding_scraper.get_price(), weighting=weight
                )

            else:
                holding = Stock(
                    symbol, holding_name, holding_scraper.get_price(), weighting=weight
                )
            holdings.append(holding)

        if len(holdings) == 0:
            return None
        else:
            return holdings
