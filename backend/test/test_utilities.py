import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities import remove_symbol


def test_remove_symbol():
    assert remove_symbol("text (symbol)") == "text"
