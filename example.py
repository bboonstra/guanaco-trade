# An example of how to use Guanaco's Trader class
import os

# Remove 'src.' for proper importing
from src.clock import MarketClock
from src.configuration import KeysPackage
from src.guanaco import Trader

# Start off by creating a key package to allow api connections to alpaca and openai
# ALPACA: https://alpaca.markets/learn/connect-to-alpaca-api/
# OPENAI API: https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key
# OPENAI ORG: https://platform.openai.com/account/organization
keys = KeysPackage(alpaca_key=os.environ['ALPACA_KEY'], alpaca_secret=os.environ['ALPACA_SECRET'],
                   openai_secret=os.environ['OPENAI_SECRET'],
                   openai_organization=os.environ['OPENAI_ORG'])

# Create a market clock and trade bot.
clock = MarketClock()
trader = Trader(keys)  # Use the previously defined key package
if clock.market_open():  # Check if it is currently trading hours using the market clock
    # Next, gather data using the trade bot about top stocks right now.
    stocks = trader.get_top_symbols()
    market_data = trader.get_market_data(stocks)
    positions = trader.get_positions()
    news = trader.get_news(stocks)
    # Ask the AI what it thinks you should trade.
    trading_advice = trader.get_advice(market_data=market_data, positions=positions, news=news,
                                       buying_power=trader.get_account().cash)
    print(trading_advice.comment)  # See what the AI has to say
    # If you'd like to automatically buy/sell based on the response, use `execute_orders`
    # receipt = trader.execute_orders(trading_advice)
    # print(receipt.content())  # See what trades were made
