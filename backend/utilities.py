import re


def remove_symbol(string):
    return re.sub(r"\([^()]*\)", "", string).strip()
