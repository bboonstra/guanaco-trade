import json
from datetime import datetime, timedelta

import openai
import requests
from alpaca_trade_api import REST
from bs4 import BeautifulSoup

from configuration import *
from data import Advice, TradeReceipt


class Trader:
    def __init__(self, keys: KeysPackage, settings: SettingsPackage = DefaultSettingsPackage,
                 prompts: PromptPackage = DefaultPromptPackage):
        self.api = REST(keys.alpaca.key, secret_key=keys.alpaca.secret, base_url=keys.alpaca.url)
        self.client = openai.OpenAI(organization=keys.openai.org, api_key=keys.openai.key)
        self.settings = settings
        self.prompts = prompts
        self.prediction_instructions = prompts.prediction()
        self.summary_instructions = prompts.summary()

    def summarize_today(self, market_data, news, positions, buying_power):
        summary_prompt = ("Market data: \n" + market_data +
                          "\nRecent news headlines: \n" + news +
                          "\nOpen positions:\n" + positions +
                          "\nBuying Power: $" + buying_power +
                          "\nReply with a summary of this day and any information that may be needed tomorrow, "
                          "2 paragraphs max.")

        response = self.client.chat.completions.create(
            model=self.settings.model,
            messages=[
                {"role": "system", "content": self.summary_instructions},
                {"role": "user", "content": summary_prompt},
            ]
        )

        return response.choices[0].message.content

    @staticmethod
    def get_top_symbols(n=25):
        url = "https://finance.yahoo.com/most-active/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', attrs={'data-test': 'quoteLink'})
        symbols = [link.text for link in links]
        return symbols[:n]

    def _calculate_gain_or_loss(self, symbol, days):
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=days + 1)
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        bars = self.api.get_bars(symbol, '1Day', start=start_str, end=end_str).df
        start_price = bars.iloc[0]['close']
        end_price = bars.iloc[-1]['close']
        gain_or_loss = end_price - start_price
        return gain_or_loss

    def get_market_data(self, stocks):
        market_data = self.api.get_latest_bars(stocks)
        formatted_data = ""
        for stock, data in market_data.items():
            thirty_change = round(abs(self._calculate_gain_or_loss(stock, 30)), 1)
            seven_change = round(abs(self._calculate_gain_or_loss(stock, 7)), 1)
            one_change = round(abs(self._calculate_gain_or_loss(stock, 2)), 1)
            thirty_arrow = "UP" if thirty_change > 0 else "DOWN"
            seven_arrow = "UP" if seven_change > 0 else "DOWN"
            one_arrow = "UP" if one_change > 0 else "DOWN"
            formatted_data += (f"{stock}-CP:{data.c},VW:{data.vw},"
                               f"1D:{one_arrow}{one_change}%,7D:{seven_arrow}{seven_change}%,"
                               f"30D:{thirty_arrow} {thirty_change}%\n")
        return formatted_data

    def get_news(self, stocks):
        news_data = self.api.get_news(stocks, limit=self.settings.news_article_limit, include_content=False)
        formatted_news = ""
        for data in news_data:
            formatted_news += f"{data.symbols[:3]}: {data.headline}\n"
        return formatted_news

    def get_positions(self):
        positions_data = self.api.list_positions()
        formatted_positions = ""
        for position in positions_data:
            formatted_positions += (f"{position.symbol} x{position.qty} (${position.current_price} ea.); "
                                    f"P/L: ${position.unrealized_pl}\n")
        return formatted_positions

    def get_advice(self, market_data: str, news: str, positions: str, buying_power: int) -> Advice:
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_prompt = ("Market data: \n" + market_data +
                       "\nRecent news headlines: \n" + news +
                       "\nOpen positions:\n" + positions +
                       "\nIt's currently: " + current_datetime +
                       "\nBuying Power: $" + str(buying_power) +
                       "\nUse the system's json format to reply.")

        response = self.client.chat.completions.create(
            model=self.settings.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.prediction_instructions},
                {"role": "user", "content": data_prompt},
            ]
        )

        adv_data = json.loads(response.choices[0].message.content)
        if 'buy' not in adv_data.keys():
            adv_data['buy'] = []
        if 'sell' not in adv_data.keys():
            adv_data['sell'] = []
        if 'comment' not in adv_data.keys():
            adv_data['comment'] = []

        advice = Advice(adv_data['buy'], adv_data['sell'], adv_data['comment'])
        return advice

    def execute_orders(self, advice: Advice) -> TradeReceipt:
        receipt = TradeReceipt("Transactions")

        for order in advice.sell:
            symbol, quantity = order['stock'], order['quantity']
            try:
                self.api.submit_order(
                    symbol=symbol,
                    qty=quantity,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                quote = self.api.get_latest_quote(symbol)
                price = quote.bp
                receipt.add_trade("SOLD", symbol, quantity, price)
            except Exception as E:
                receipt.add_entry(f"Purchase of {symbol} x{quantity} failed; {E}")

        for order in advice.buy:
            symbol, quantity = order['stock'], order['quantity']
            try:
                self.api.submit_order(
                    symbol=symbol,
                    qty=quantity,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                quote = self.api.get_latest_quote(symbol)
                price = quote.bp
                receipt.add_trade("BOUGHT", symbol, quantity, price)
            except Exception as E:
                receipt.add_entry(f"Purchase of {symbol} x{quantity} failed; {E}")

        receipt.finalize()
        return receipt

    def get_account(self):
        return self.api.get_account()
