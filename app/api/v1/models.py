from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List

import pytz
import requests
from pydantic import BaseModel
from pymongo.collection import Collection


class CurrencyType(Enum):

    """Currency types: real or created by user."""
    REAL = "real"
    CUSTOM = "custom"
    BACKING = "backing"


class CurrencyItem(BaseModel):

    """Representation of a currency.

    Attributes:
        code (str): Currency code.
        rate_usd (float): Conversion rate in USD.
        currency_type (CurrencyType): Currency type (real or custom).
    """
    code: str
    rate_usd: float
    currency_type: str

    def __init__(self, code: str, rate_usd: float, currency_type: str) -> None:
        super().__init__(code=code, rate_usd=rate_usd, currency_type=currency_type)


class CurrencyList(BaseModel):

    """Representation of a list of currencies.

    Attributes:
        list_of_currencies(List[CurrencyItem]): List of currency items.
    """
    list_of_currencies: List[CurrencyItem]

    def __init__(self, list_of_currencies: List[CurrencyItem]):
        super().__init__(list_of_currencies=list_of_currencies)

    def get_currency_list(self) -> list:
        """Returns a list of currency codes."""

        return [a.code for a in self.list_of_currencies]

    def list_currency_items(self) -> List[CurrencyItem]:
        """Returns a list of currency items."""

        return [a for a in self.list_of_currencies]

    def get_real_currencies(self) -> CurrencyList:
        """Returns a CurrencyList of real currencies."""

        return CurrencyList(
            [
                a
                for a in self.list_of_currencies
                if a.currency_type == CurrencyType.REAL.value
            ]
        )

    def get_currency_rate(self) -> dict:

        """Returns a dict with currency code as key and usd_rate as values."""
        return {i.code: i.rate_usd for i in self.list_currency_items()}


class DatabaseCurrencyList(BaseModel):

    """Database representation (document) containing created/updated time and CurrencyList items."""
    update_time: datetime
    currencies: CurrencyList

    def __init__(
            self,
            currencies: CurrencyList,
            update_time: datetime = datetime.now().astimezone(pytz.utc),
    ) -> None:
        super().__init__(update_time=update_time, currencies=currencies)
        self.update_time = datetime.now().astimezone(pytz.utc)
        self.currencies = currencies

    def update_timestamp(self) -> None:
        """Updates the update_time attribute."""

        self.update_time = datetime.now().astimezone(pytz.utc)

    def return_currency_list_obj(self) -> CurrencyList:
        """Returns a CurrencyList containing all currencies inside the DatabaseCurrencyList object."""

        return CurrencyList(self.currencies.get("list_of_currencies"))

    def get_currencies_list(self, all_currencies: bool = False) -> list:
        """Returns a list of currencies (all or only 'real') inside the DatabaseCurrencyList object."""

        if all_currencies:
            return self.return_currency_list_obj().get_currency_list()
        return self.return_currency_list_obj().get_real_currencies().get_currency_list()


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
    def get_conversion(
            cls, url: str, usd_rate_collection: Collection, tracked_collection: Collection
    ) -> None:
        """Updates usd_rate_collection based on a tracked_collection."""
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
    def get_conversion(
            cls, url: str, usd_rate_collection: Collection, tracked_collection: Collection
    ) -> None:
        """Updates usd_rate_collection based on a tracked_collection."""

        response_json = requests.get(url).json()
        rates_dic = {
            value["code"]: value["bid"] for key, value in response_json.items()
        }
        last_doc = usd_rate_collection.find_one({}, sort=[("_id", -1)])
        del last_doc["_id"]
        c = last_doc.get("currencies").get("list_of_currencies")
        for i in c:
            if i.get("code") in rates_dic.keys():
                i["rate_usd"] = rates_dic.get(i.get("code"))
        usd_rate_collection.insert_one(last_doc)
