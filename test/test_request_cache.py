import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from request_cache import RequestCache

# Test for RequestCache class


def test_request_cache_init():
    request_cache = RequestCache()
    assert request_cache._cache == {}


# Note: The following test is commented out because it makes a real HTTP request.
# Uncomment it to run the test, but be aware that it may fail if there are network issues.


def test_request_cache_get():
    request_cache = RequestCache()
    response = request_cache.get("https://www.google.com")
    assert response.status_code == 200
