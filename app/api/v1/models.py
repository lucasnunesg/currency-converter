import requests
from datetime import datetime
from pymongo import collection

import pytz
from pydantic import BaseModel

from abc import ABC, abstractmethod


class CurrencyResponse(BaseModel):
    name: str
    rate_usd: float


class CurrencyAPI(ABC):
    base_url: str

    @classmethod
    @abstractmethod
    def url_builder(cls, currency_list: list) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_conversion(cls, url: str, db: collection.Collection) -> None:
        pass


class EconomiaAwesomeAPI(CurrencyAPI):
    base_url = "http://economia.awesomeapi.com.br/json/last/"

    def __init__(self, base_url=None) -> None:
        if base_url is None:
            self.base_url = "http://economia.awesomeapi.com.br/json/last/"
        else:
            self.base_url = base_url

    @classmethod
    def url_builder(cls, currency_list: list) -> str:
        url = ""
        for currency in currency_list:
            url = cls.base_url + currency + "-USD,"
        return url[:-1]

    @classmethod
    def get_conversion(cls, url: str, db: collection.Collection) -> None:
        response_json = requests.get(url).json()
        utc_time = datetime.now().astimezone(pytz.utc)
        currency_conversion_dict = {"Update time": utc_time}
        for item in response_json:
            currency_conversion_dict.update({item: response_json.get(item).get("bid")})
        db.insert_one(currency_conversion_dict)
