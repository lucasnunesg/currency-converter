from pymongo import MongoClient
from pymongo.collection import Collection
from app.api.v1.models import (
    CurrencyAPI,
    EconomiaAwesomeAPI,
    CurrencyItem,
    CurrencyType,
)
from typing import Type
from datetime import datetime
import pytz


utc_time_now = datetime.now().astimezone(pytz.utc)

currencies = [
    CurrencyItem(
        code="BRL", rate_usd=0, type=CurrencyType.REAL.value, update_time=utc_time_now
    ),
    CurrencyItem(
        code="EUR", rate_usd=0, type=CurrencyType.REAL.value, update_time=utc_time_now
    ),
    CurrencyItem(
        code="BTC", rate_usd=0, type=CurrencyType.REAL.value, update_time=utc_time_now
    ),
    CurrencyItem(
        code="ETH", rate_usd=0, type=CurrencyType.REAL.value, update_time=utc_time_now
    ),
    CurrencyItem(
        code="USD", rate_usd=1, type=CurrencyType.REAL.value, update_time=utc_time_now
    ),
]


def create_currency_list_document():
    coll = mongodb_connect(collection="currency_list_info")
    coll.insert_many([obj.dict() for obj in currencies])
    return coll


def update_currency_rate_document(collection: Collection) -> None:
    collection.insert_many([obj.dict() for obj in currencies])


def mongodb_connect(
    database: str = "database",
    collection: str = "collection",
    host: str = "localhost",
    port: int = 27017,
) -> Collection:
    """
    Returns a pymongo collection connected to MongoDB

            Parameters:
                    database (str): Name of the database
                    collection (str): Name of the collection
                    host (str): Host address of the MongoDB server
                    port (int): Port number


            Returns:
                    collection (pymongo.collection.Collection): MongoDB collection
    """

    client = MongoClient(host=host, port=port)

    database = client[f"{database}"]

    collection = database[f"{collection}"]

    return collection


def update_conversion_collection(
    db: Collection,
    api: Type[CurrencyAPI] = EconomiaAwesomeAPI,
    currency_list: list = tuple([c.code for c in currencies if c.code != "USD"]),
) -> None:
    """
    Creates a new document in the provided collection with updated currency conversion values based on the provided
    API instance.

            Parameters:
                    db (pymongo.collection.Collection): pymongo collection to be updated (new document will be created)
                    api (Type[CurrencyAPI]): API class (must be a valid CurrencyAPI subclass) to fetch data
                    currency_list (list): List o currency names to be added to the database
    """
    url = api.url_builder(currency_list)
    api.get_conversion(url, db)


if __name__ == "__main__":
    currency_rate_document = mongodb_connect(collection="currency_list_info")
    update_currency_rate_document(currency_rate_document)
    update_conversion_collection(db=currency_rate_document)
