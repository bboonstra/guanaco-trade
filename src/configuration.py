import os
from typing import Optional, Union


class ConfigurationPackage:
    def __init__(self):
        pass


class SettingsPackage(ConfigurationPackage):
    ALLOWED_GPT_MODELS = [
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-4-32k-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-16k-0613",
    ]

    def __init__(self, gpt_model: str,
                 news_article_limit: int = 15, symbol_limit: int = 25):
        super().__init__()
        if gpt_model not in self.ALLOWED_GPT_MODELS:
            raise ValueError(f"Invalid gpt_model string. Must be one of: {self.ALLOWED_GPT_MODELS}")
        if news_article_limit < 0:
            raise ValueError(f"New article limit must be positive.")
        if news_article_limit > 50:
            raise ValueError(f"New article limit cannot be more than 50.")
        if symbol_limit < 1:
            raise ValueError(f"Symbol limit must be 1 or more.")
        if symbol_limit > 50:
            raise ValueError(f"Symbol limit cannot be more than 50.")
        self.model = gpt_model
        self.news_article_limit = news_article_limit
        self.symbol_limit = symbol_limit


class AlpacaKeyPackage:
    def __init__(self, key: str, secret: str, paper: bool = True):
        self.key = key
        self.secret = secret
        self.url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"


class OpenaiKeyPackage:
    def __init__(self, key: str, organization: str):
        self.key = key
        self.org = organization


class KeysPackage(ConfigurationPackage):
    def __init__(self, alpaca_key: str, alpaca_secret: str,
                 openai_secret: str, openai_organization: str,
                 paper: bool = True):
        super().__init__()

        self.alpaca = AlpacaKeyPackage(alpaca_key, alpaca_secret, paper)
        self.openai = OpenaiKeyPackage(openai_secret, openai_organization)


class PromptPackage(ConfigurationPackage):
    def __init__(self, prediction_message: Optional[Union[str, os.PathLike]] = None,
                 summary_message: Optional[Union[str, os.PathLike]] = None):
        super().__init__()
        self._prediction_message = prediction_message
        self._summary_message = summary_message

    def prediction(self):
        if isinstance(self._prediction_message, str):
            # Check if the string is a file path
            if os.path.isfile(self._prediction_message):
                # Read the content of the file
                with open(self._prediction_message, 'r') as file:
                    return file.read()
            else:
                # Assume it's a string message
                return self._prediction_message
        else:
            f = __file__.replace("configuration.py", "")
            with open(f+"commands/predict.txt", "r") as prompt:
                return prompt.read()

    def summary(self):
        if isinstance(self._summary_message, str):
            # Check if the string is a file path
            if os.path.isfile(self._summary_message):
                # Read the content of the file
                with open(self._summary_message, 'r') as file:
                    return file.read()
            else:
                # Assume it's a string message
                return self._summary_message
        else:
            f = __file__.replace("configuration.py", "")
            with open(f + "commands/summarize.txt", "r") as prompt:
                return prompt.read()


DefaultPromptPackage = PromptPackage()
DefaultSettingsPackage = SettingsPackage(gpt_model="gpt-3.5-turbo-0125")
