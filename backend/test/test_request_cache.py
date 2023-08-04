import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
from request_cache import RequestCache


def test_request_cache():
    with patch("requests.get") as mocked_get:
        mocked_get.return_value = "Mocked response"
        cache = RequestCache()

        response1 = cache.get("https://example.com")
        response2 = cache.get("https://example.com")

        assert mocked_get.call_count == 1

        assert response1 == "Mocked response"
        assert response2 == "Mocked response"
