import json
from typing import Type, List

import requests
from datetime import datetime
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
    type: str


class CurrencyList:
    list: List[CurrencyItem]
    update_time: datetime

    def __init__(self, list_currencies: List[CurrencyItem]):
        self.list = list_currencies
        self.update_time = datetime.now().astimezone(pytz.utc)

    def get_currency_list(self):
        return [a.code for a in self.list]

    def list_currency_items(self):
        return [a for a in self.list]


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
    def get_conversion(
        cls, url: str, rate_coll: Collection, track_coll: Collection
    ) -> None:
        pass


class EconomiaAwesomeAPI(CurrencyAPI):
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
        print("RESPONSE JSON: ", response_json)
        extract_collection = rate_coll.find_one({})
        print("EXTRACT: ", extract_collection)
        print()
        print("------")
        print()

        track_document_currency_list = [doc for doc in track_coll.find({})]
        currencies_to_be_updated = []

        for item in response_json:
            item_code = response_json[item].get("code")
            item_rate = response_json[item].get("bid")
            item_type = CurrencyType.REAL.value

            for element in track_document_currency_list:
                element_code = element.get("code")
                if item_code == element_code:
                    element["rate_usd"] = item_rate

        print("FINAL ADD LIST: ", track_document_currency_list)
        print(type(track_document_currency_list))
        print(type(track_document_currency_list[1]))

        rate_coll.insert_one(
            {
                "update_time": datetime.now().astimezone(pytz.utc),
                "currencies": track_document_currency_list,
            }
        )

        print()

        print("Updated conversion rates (USD) successfully")
