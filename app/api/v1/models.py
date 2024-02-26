from typing import Type

import requests
from datetime import datetime
from pymongo import collection

import pytz
from pydantic import BaseModel
from enum import Enum
from abc import ABC, abstractmethod


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
    update_time: datetime


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
    def get_conversion(cls, url: str, db: collection.Collection) -> None:
        response_json = requests.get(url).json()
        for item in response_json:
            db.update_one(
                {"code": response_json[item].get("code")},
                {"$set": {"rate_usd": response_json[item].get("bid")}},
            )
        print("Updated conversion rates (USD) successfully")
