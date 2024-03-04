from abc import ABC, abstractmethod

import requests


class CurrencyApiInterface(ABC):

    """Interface to establish contract to implement external interfaces to fetch conversion rates."""
    base_url: str

    @classmethod
    @abstractmethod
    def url_builder(cls, currency_list: list) -> str:
        """Returns in a single url all the conversion rates required (relative to USD)."""
        pass

    @classmethod
    @abstractmethod
    def get_conversion(cls, url: str, currency_list: list) -> dict:
        """Returns updated conversions dictionary related to USD."""
        pass


class EconomiaAwesomeAPI(CurrencyApiInterface):
    base_url: str = "http://economia.awesomeapi.com.br/json/last/"

    def __init__(self, base_url=None) -> None:
        if base_url is None:
            self.base_url = "http://economia.awesomeapi.com.br/json/last/"
        else:
            self.base_url = base_url

    @classmethod
    def url_builder(cls, currency_list: list) -> str:
        """Returns in a single url all the conversion rates required (relative to USD)."""

        url = cls.base_url
        for currency in currency_list:
            url += currency + "-USD,"
        return url[:-1]

    @classmethod
    def get_conversion(cls, url: str, currency_list: list) -> dict:
        """Returns updated conversions dictionary related to USD."""
        response = requests.get(url)
        data = response.json()
        currency_rates_updated = {value["code"]: value['bid'] for value in data.values()}
        return currency_rates_updated
