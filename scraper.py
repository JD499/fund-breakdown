import requests
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, symbol):
        self._symbol = symbol

    def get_price(self):
        url = f"https://finance.yahoo.com/quote/{self._symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        price = soup.find("fin-streamer", {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"})["value"] # type: ignore  # noqa: E501
        return float(price) # type: ignore
    
    def get_name(self):
        url = f"https://finance.yahoo.com/quote/{self._symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        name = soup.find("h1", {"class": "D(ib) Fz(18px)"}).text # type: ignore
        return name
    
    def get_holdings(self):
        url = f"https://finance.yahoo.com/quote/{self._symbol}/holdings?p={self._symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # Find the table containing the holdings information
        table = soup.find('table', {'class': 'W(100%) M(0) BdB Bdc($seperatorColor)'})
        if table is None:
            return None
    
        # Extract the rows from the table (excluding the header row)
        rows = table.find_all('tr')[1:]   # type: ignore
    
        # Extract the holdings information from each row and store it in a dictionary
        holdings_info = {}
        for row in rows:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            holdingName, symbol, weight = cols[0], cols[1], cols[2]
            # if symbol is BRK.B, change to BRK-B to match Yahoo Finance, likewise 
            # if symbol is BRK.A, change to BRK-A
            if symbol == 'BRK.B':
                symbol = 'BRK-B'
            elif symbol == 'BRK.A':
                symbol = 'BRK-A'
            weight = float(weight[:-1])
            holdings_info[symbol] = {'name': holdingName, 'weight': weight}    

        # Return the dictionary of holdings information
        if len(holdings_info) == 0:
            return None
        else:
            return holdings_info