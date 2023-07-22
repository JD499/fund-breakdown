import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, symbol):
        """
        Initializes a new instance of the Scraper class with the specified symbol.

        Args:
            symbol (str): The symbol of the fund to scrape.
        """
        self._symbol = symbol

    def _make_request(self, url):
        """
        Sends an HTTP GET request to the specified URL and returns the response.

        Args:
            url (str): The URL to send the request to.

        Returns:
            requests.Response: The response to the request.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
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
        return name

    def get_holdings(self):
        """
        Retrieves the holdings of the fund.

        Returns:
            list of tuples: A list of tuples representing the holdings of the fund.
            Each tuple contains the symbol, name, and weight of a holding.
            If the holdings cannot be retrieved, returns None.
        """
        url = (
            f"https://finance.yahoo.com/quote/{self._symbol}/holdings?p={self._symbol}"
        )
        soup = self._get_soup(url)

        table = soup.find("table", {"class": "W(100%) M(0) BdB Bdc($seperatorColor)"})
        if table is None:
            return None

        rows = table.find_all("tr")[1:]  # type: ignore

        holdings_info = []
        for row in rows:
            cols = row.find_all("td")
            cols = [col.text.strip() for col in cols]
            holding_name, symbol, weight = cols[0], cols[1], cols[2]

            if symbol == "BRK.B":
                symbol = "BRK-B"
            elif symbol == "BRK.A":
                symbol = "BRK-A"
            weight = float(weight[:-1])
            holdings_info.append((symbol, holding_name, weight))

        if len(holdings_info) == 0:
            return None
        else:
            return holdings_info
