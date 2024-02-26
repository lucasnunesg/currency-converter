from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from app.api.v1.models import (
    CurrencyAPI,
    EconomiaAwesomeAPI,
    CurrencyItem,
    CurrencyType,
    CurrencyList,
)
from typing import Type
from datetime import datetime
import pytz


def utc_time_now():
    return datetime.now().astimezone(pytz.utc)


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


def get_last_updated_document(collection: Collection) -> dict:
    return collection.find_one({}, sort=[("_id", -1)])


def get_currency_from_document(doc: dict, currency_code: str) -> dict:
    currencies_dict = doc.get("currencies")
    for item in currencies_dict:
        if item["code"] == currency_code:
            return item


def create_tracked_currencies_document() -> Collection:
    default_currencies = [
        CurrencyItem(code="BRL", rate_usd=0, type=CurrencyType.REAL.value),
        CurrencyItem(code="EUR", rate_usd=0, type=CurrencyType.REAL.value),
        CurrencyItem(code="BTC", rate_usd=0, type=CurrencyType.REAL.value),
        CurrencyItem(code="ETH", rate_usd=0, type=CurrencyType.REAL.value),
        CurrencyItem(code="USD", rate_usd=1, type=CurrencyType.REAL.value),
    ]

    coll = mongodb_connect(database="currency-list", collection="tracked-currencies")
    if coll.count_documents({}) == 0:
        coll.insert_many([obj.dict() for obj in default_currencies])
    return coll


def from_tracked_to_rate(source: Collection, destination: Collection) -> None:
    add_list = [doc for doc in source.find({})]
    destination.insert_one({"update_time": utc_time_now(), "currencies": add_list})


def get_list_of_currencies(tracked_collection: Collection) -> list:
    currencies_list = []
    # doc = {i for i in tracked_collection.find({})}
    # currencies_dict = doc.get("currencies")
    for doc in tracked_collection.find({}):
        print(doc)
        print(type(doc))
        currencies_dict = doc.get("currencies")
        for i in currencies_dict:
            currencies_list.append(i.get("code"))
        # currencies_list.append(doc["currencies"]["code"])
        currencies_list = list(set(currencies_list))
        if "USD" in currencies_list:
            currencies_list.remove("USD")
    return currencies_list


def add_tracked_currency(
    code: str, rate_usd: float, collection: Collection
) -> Collection:
    collection.insert_one(
        CurrencyItem(
            code=code, rate_usd=rate_usd, Type=CurrencyType.CUSTOM.value
        ).dict()
    )
    return collection


def create_currency_rate_document(
    collection: Collection, currency_list: CurrencyList
) -> None:
    """Takes a collection and currency list (CurrencyList object) and inserts into the document"""
    object_dict_list = [obj.dict() for obj in currency_list.list_currency_items()]
    collection.insert_one(
        {"update_time": utc_time_now(), "currencies": object_dict_list}
    )


def update_conversion_collection(
    rate_coll: Collection,
    track_coll: Collection,
    api: Type[CurrencyAPI] = EconomiaAwesomeAPI,
) -> None:
    """
    Creates a new document in the provided collection with updated currency conversion values based on the provided
    API instance.

            Parameters:
                    rate_coll (Collection): pymongo collection of the currency rates
                    track_coll (Collection): pymongo collection of the currency list
                    api (Type[CurrencyAPI]): API class (must be a valid CurrencyAPI subclass) to fetch data
    """

    if rate_coll.count_documents({}) == 0:
        from_tracked_to_rate(track_coll, rate_coll)

    url = api.url_builder(get_list_of_currencies(rate_coll))
    api.get_conversion(url, rate_coll, track_coll)


if __name__ == "__main__":
    # Connecting to the database and creating the "currency_rate collection"
    currency_rate_collection = mongodb_connect(collection="currency_rate")

    # Creates the document with blank rates_USD but with default currencies
    tracked_currencies_collection = create_tracked_currencies_document()
    update_conversion_collection(
        rate_coll=currency_rate_collection, track_coll=tracked_currencies_collection
    )

    # update_conversion_collection(collection=tracked_currencies_collection)
    """create_currency_rate_document(
        collection=currency_rate_collection, currency_list=CurrencyList(currencies)
    )"""

"""
    # Updates the conversion rates based on the registered currencies on DB
    a = get_last_updated_document(currency_rate_collection, "update_time")
    b = get_currency_from_document(a, "BRL")
    print(a)
    print(type(a))
    print(b)
    print(type(b))
    print([b["rate_usd"]])"""
