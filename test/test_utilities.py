import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from utilities import remove_symbol

# Test for utilities


def test_remove_symbol():
    assert remove_symbol("text (symbol)") == "text"
