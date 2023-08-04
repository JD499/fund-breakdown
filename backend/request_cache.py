from functools import lru_cache

import requests


class RequestCache:
    def __init__(self):
        self._cache = self._cached_get

    @lru_cache(maxsize=100)
    def _cached_get(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        return response

    def get(self, url):
        return self._cache(url)
