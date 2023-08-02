import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
from request_cache import RequestCache


# Test for RequestCache class


def test_request_cache():
    with patch("requests.get") as mocked_get:
        mocked_get.return_value = "Mocked response"
        cache = RequestCache()

        # Call the get method twice with the same URL
        response1 = cache.get("https://example.com")
        response2 = cache.get("https://example.com")

        # Check that the requests.get method was called only once
        assert mocked_get.call_count == 1

        # Check that the responses are equal to the mocked response
        assert response1 == "Mocked response"
        assert response2 == "Mocked response"
