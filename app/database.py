from json import dumps

from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pprint import pprint

from api.v1.models import (
    CurrencyApiInterface,
    EconomiaAwesomeAPI,
    CurrencyItem,
    CurrencyType,
    CurrencyList,
    CurrencyResponse,
)
from typing import Type, List
from datetime import datetime
import pytz


def utc_time_now():
    return datetime.now().astimezone(pytz.utc)


def mongodb_connect(
    database: str = "database",
    collection: str = "collection",
    host: str = "database",  # database for docker, localhost for local
    port: int = 27017,
) -> Collection:
    """
    Returns a pymongo collection connected to MongoDB

            Parameters:
                    database (str): database name
                    collection (str): collection name
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
    """Returns the last document added to a given collection"""
    return collection.find_one({}, sort=[("_id", -1)])


def get_cursor_remove_fields(collection: Collection, fields: List) -> Cursor:
    """Returns a cursor object of a collection removing the fields specified on the given list"""
    fields_to_be_removed = {f"{field}": 0 for field in fields}
    return collection.find({}, fields_to_be_removed)


def parse_last_rate_document_to_object(rate_coll: Collection) -> CurrencyList:
    dic = get_last_updated_document(rate_coll)
    del dic["_id"]
    currency_list = CurrencyList(dic.get("currencies"))
    return currency_list


def from_tracked_to_rate(
    tracked_coll: Collection, rate_coll: Collection
) -> CurrencyList:
    """Updates currencies of rate_coll based on all documents inside tracked_coll, and returns a CurrencyList object"""
    all_documents_no_id = get_cursor_remove_fields(tracked_coll, ["_id"])
    currency_item_list = [CurrencyItem.model_validate(i) for i in all_documents_no_id]
    currency_list = CurrencyList(currency_item_list)
    rate_coll.insert_one(currency_list.to_tracked_currencies_model())
    dic = get_last_updated_document(rate_coll)
    del dic["_id"]
    currency_list = CurrencyList(dic.get("currencies"))
    return currency_list


def update_conversion_collection(
    rate_coll: Collection,
    track_coll: Collection,
    api: Type[CurrencyApiInterface] = EconomiaAwesomeAPI,
) -> None:
    """
    Takes all registered currencies on track_coll and creates a new document in rate_coll with updated currency
    conversion values based on the provided API instance.

            Parameters:
                    rate_coll (Collection): pymongo collection of the currency rates
                    track_coll (Collection): pymongo collection of the currency list
                                            (will be used to fetch all registered currencies)
                    api (CurrencyApiInterface): API class (must be a valid CurrencyAPI subclass) to fetch external data
    """

    currency_list_object = from_tracked_to_rate(track_coll, rate_coll)
    real_currency_objects = currency_list_object.get_real_currencies()
    currency_list = real_currency_objects.get_currency_list()
    url = api.url_builder(currency_list)

    api.get_conversion(url, rate_coll, track_coll)

    last_two_documents = rate_coll.find().sort([("_id", -1)]).limit(2)

    last_two_documents_list = list(last_two_documents)
    penultimate_document = last_two_documents_list[1].get("_id")
    rate_coll.delete_one({"_id": penultimate_document})


def check_empty_collection(collection: Collection) -> bool:
    """Checks if a given collection is empty (0 documents)"""
    if collection.count_documents({}) == 0:
        return True
    return False


def populate_tracked_currencies(tracked_collection: Collection) -> None:
    """Populates de tracked currencies database based on the default list: BRL, EUR, BTC, ETH, USD"""
    default_currencies = CurrencyList(
        [
            CurrencyItem(code="BRL", rate_usd=0, currency_type=CurrencyType.REAL.value),
            CurrencyItem(code="EUR", rate_usd=0, currency_type=CurrencyType.REAL.value),
            CurrencyItem(code="BTC", rate_usd=0, currency_type=CurrencyType.REAL.value),
            CurrencyItem(code="ETH", rate_usd=0, currency_type=CurrencyType.REAL.value),
            CurrencyItem(
                code="USD", rate_usd=1, currency_type=CurrencyType.BACKING.value
            ),
        ]
    )
    tracked_collection.insert_many(
        [i.dict() for i in default_currencies.list_currency_items()]
    )


def init_databases() -> List[Collection]:
    """Initialize Rate and Tracked Currencies databases with default currencies"""
    rate_collection = mongodb_connect(database="database", collection="currency_rate")
    tracked_collection = mongodb_connect(
        database="database", collection="tracked_currencies"
    )
    if check_empty_collection(tracked_collection):
        populate_tracked_currencies(tracked_collection)
    return [rate_collection, tracked_collection]


[currency_rate_collection, tracked_currencies_collection] = init_databases()

update_conversion_collection(
    rate_coll=currency_rate_collection,
    track_coll=tracked_currencies_collection,
    api=EconomiaAwesomeAPI,
)

if __name__ == "__main__":
    [currency_rate_collection, tracked_currencies_collection] = init_databases()
    update_conversion_collection(
        rate_coll=currency_rate_collection,
        track_coll=tracked_currencies_collection,
        api=EconomiaAwesomeAPI,
    )

    dic = get_last_updated_document(currency_rate_collection)
    lista_currencies = dic.get("currencies")
    lista_sem_id = [i for i in lista_currencies if i != "_id"]
    cursor = currency_rate_collection.find().sort([("_id", -1)]).limit(1)
    for i in lista_sem_id:
        i.pop("_id")
    print("LISTA SEM ID")
    pprint(lista_sem_id)
    b = 0
    for i in lista_sem_id:
        if i.get("code").upper() == "BRL":
            b = i.get("rate_usd")
    print(b)

    """
    def parse_last_rate_document_to_object(rate_coll: Collection) -> CurrencyList:
    dic = get_last_updated_document(rate_coll)
    del dic["_id"]
    currency_list = CurrencyList(dic.get("currencies"))
    return currency_list"""
    """
    import json


    all_documents_no_id = get_cursor_remove_fields(
        tracked_currencies_collection, ["_id"]
    )
    currency_item_list = [CurrencyItem.model_validate(i) for i in all_documents_no_id]
    currency_list = CurrencyList(currency_item_list)
    pprint(currency_list)
    print(currency_list)
    print(type(currency_list))
    last_doc = get_last_updated_document(tracked_currencies_collection)
    test_id = last_doc["_id"]
    print("DOC: ", last_doc)
    print("TEST ID: ", test_id)
    test = CurrencyItem(
        last_doc.get("code"), last_doc.get("rate_usd"), last_doc.get("currency_type")
    )
    print("TEST ITEM: ", test)
    print(type(test))
    del last_doc["_id"]
    test2 = CurrencyItem(**last_doc)
    print("TEST ITEM2: ", test2)
    print(type(test2))
    """
