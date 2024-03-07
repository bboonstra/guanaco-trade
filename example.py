import os

from clock import MarketClock
from configuration import KeysPackage
from guanaco import Trader

keys = KeysPackage(alpaca_key=os.environ['ALPACA_KEY'], alpaca_secret=os.environ['ALPACA_SECRET'],
                   openai_secret=os.environ['OPENAI_SECRET'],
                   openai_organization=os.environ['OPENAI_ORG'])
trader = Trader(keys)
clock = MarketClock()
stocks = trader.get_top_symbols()
market_data = trader.get_market_data(stocks)
positions = trader.get_positions()
news = trader.get_news(stocks)
trading_advice = trader.get_advice(market_data=market_data, positions=positions, news=news, buying_power=100000)

print(trading_advice.comment)
print(trading_advice.buy)
print(trading_advice.sell)

receipt = trader.execute_orders(advice=trading_advice)
print(receipt)
