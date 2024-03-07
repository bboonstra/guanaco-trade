class Advice:
    def __init__(self, buy, sell, comment):
        self.buy = buy
        self.sell = sell
        self.comment = comment

    def symbols(self):
        return [order['stock'] for order in self.buy] + [order['stock'] for order in self.sell]

class Receipt:
    def __init__(self):
        self.total_price = 0
