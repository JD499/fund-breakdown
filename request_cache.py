import requests


class RequestCache:
    def __init__(self):
        self._cache = {}

    def get(self, url):
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