import re


def remove_symbol(string):
    """
    Removes any text within parentheses and leading/trailing whitespace from a string.

    Args:
        string (str): The string to remove text from.

    Returns:
        str: The modified string with text within parentheses and leading/trailing 
        whitespace removed.
    """
    return re.sub(r"\([^()]*\)", "", string).strip()
