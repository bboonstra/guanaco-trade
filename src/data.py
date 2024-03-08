from datetime import datetime
from copy import deepcopy


class Advice:
    def __init__(self, buy, sell, comment):
        self.buy = buy
        self.sell = sell
        self.comment = comment

    def symbols(self):
        return [order['stock'] for order in self.buy] + [order['stock'] for order in self.sell]


class ForgeryError(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class Receipt:
    def __init__(self, header):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._content = ""
        self.header = header
        self.final = False
        self._copy = None
        self._transcript = None

    def add_entry(self, entry):
        self._content += f"\n{datetime.now().strftime("%H:%M:%S")} - {entry}"

    def content(self):
        if not self.final:
            self._transcript = (f"\033[1;4m {self.header} \033[0m\n"
                                f"{self.timestamp}\n"
                                f"---------------"
                                f"{self._content}")

        return self._transcript

    def finalize(self):
        if self.final:
            return self._transcript
        self._copy = deepcopy(self)

        self._transcript = (f"\033[1;4m {self.header} \033[0m\n"
                      f"{self.timestamp}\n"
                      f"---------------"
                      f"{self._content}")
        self.final = True

        return self._transcript

    def copy(self):
        if self._copy:
            return self._copy
        else:
            return deepcopy(self)

    def __setattr__(self, name, value):
        try:
            if self.final:
                raise ForgeryError("This receipt has been printed and is final; "
                                   "To edit a final receipt, make a copy()")
            else:
                super().__setattr__(name, value)
        except AttributeError:
            super().__setattr__(name, value)


class TradeReceipt(Receipt):
    def __init__(self, header):
        super().__init__(header)

    def add_trade(self, trade_type, stock_symbol, quantity, cost):
        color = "\033[31m" if trade_type == "SOLD" else "\033[32m"
        self.add_entry(f"{color}{trade_type.upper()}\033[0m "
                       f"{stock_symbol} x{quantity} @ ${cost} per share")

