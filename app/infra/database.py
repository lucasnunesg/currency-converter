from pymongo import MongoClient
from pymongo.collection import Collection
from app.api.v1.models import CurrencyAPI, EconomiaAwesomeAPI
from typing import Type

DEFAULT_CURRENCIES = ("BRL", "EUR", "BTC", "ETH")


def mongodb_connect(
    database: str = "database",
    collection: str = "collection",
    host: str = "localhost",
    port: int = 27017,
) -> Collection:
    client = MongoClient(host=host, port=port)

    database = client[f"{database}"]

    collection = database[f"{collection}"]

    return collection


def update_conversion_collection(
    db: Collection,
    api: Type[CurrencyAPI] = EconomiaAwesomeAPI,
    currency_list: list = DEFAULT_CURRENCIES,
) -> None:
    url = api.url_builder(currency_list)
    api.get_conversion(url, db)


if __name__ == "__main__":
    db = mongodb_connect()
    update_conversion_collection(db=db)
