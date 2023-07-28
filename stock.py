class Stock:
    def __init__(self, symbol):
        self._symbol = symbol
        self._name = ""
        self._price = 0
        self._shares = 0
        self._weighting = 0
        self._value = 0

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def shares(self):
        return self._shares

    @shares.setter
    def shares(self, value):
        self._shares = value

    @property
    def weighting(self):
        return self._weighting

    @weighting.setter
    def weighting(self, value):
        self._weighting = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
