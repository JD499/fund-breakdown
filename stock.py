class Stock:
    def __init__(self, symbol, name, price, weighting=None):
        self._symbol = symbol
        self._name = name
        self._price = price
        self._weighting = weighting

    @property
    def symbol(self):
        return self._symbol

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def weighting(self):
        return self._weighting

    @weighting.setter
    def weighting(self, value):
        self._weighting = value