import json
from typing import List

import requests
from pymongo.collection import Collection


import pytz
from pydantic import BaseModel
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime


class CurrencyType(Enum):
    """Currency types: real or created by user"""

    REAL = "real"
    CUSTOM = "custom"
    BACKING = "backing"


class CurrencyItem(BaseModel):
    """
    Representation of a currency

            Attributes:
                    code (str): Currency code (3 letters)
                    rate_usd (float): Conversion rate in USD
                    type (CurrencyType): Currency type (real or custom)
    """

    code: str
    rate_usd: float
    currency_type: str

    def __init__(self, code: str, rate_usd: float, currency_type: str) -> None:
        super().__init__(code=code, rate_usd=rate_usd, currency_type=currency_type)


class CurrencyList(BaseModel):
    list_of_currencies: List[CurrencyItem]

    def __init__(self, list_of_currencies: List[CurrencyItem]):
        super().__init__(list_of_currencies=list_of_currencies)

    def get_currency_list(self) -> list:
        return [a.code for a in self.list_of_currencies]

    def list_currency_items(self) -> list:
        return [a for a in self.list_of_currencies]

    def to_tracked_currencies_model(self) -> dict:
        utc_time_now = datetime.now().astimezone(pytz.utc)
        return {
            "update_time": utc_time_now,
            "currencies": [dict(i) for i in self.list_currency_items()],
        }

    def get_real_currencies(self):
        return CurrencyList(
            [
                a
                for a in self.list_of_currencies
                if a.currency_type == CurrencyType.REAL.value
            ]
        )


class CurrencyResponse(BaseModel):
    name: str
    rate_usd: float


class CurrencyApiInterface(ABC):
    base_url: str

    @classmethod
    @abstractmethod
    def url_builder(cls, currency_list: list) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_conversion(
        cls, url: str, rate_coll: Collection, track_coll: Collection
    ) -> None:
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
        url = cls.base_url
        for currency in currency_list:
            url += currency + "-USD,"
        return url[:-1]

    @classmethod
    def get_conversion(
        cls, url: str, rate_coll: Collection, track_coll: Collection
    ) -> None:
        response_json = requests.get(url).json()

        track_document_currency_list = [doc for doc in track_coll.find({})]

        for item in response_json:
            item_code = response_json[item].get("code")
            item_rate = response_json[item].get("bid")

            for element in track_document_currency_list:
                element_code = element.get("code")
                if item_code == element_code:
                    element["rate_usd"] = item_rate

        rate_coll.insert_one(
            {
                "update_time": datetime.now().astimezone(pytz.utc),
                "currencies": track_document_currency_list,
            }
        )
