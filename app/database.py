from pymongo import MongoClient
from pymongo.collection import Collection
from pprint import pprint

from api.v1.models import (
    CurrencyApiInterface,
    EconomiaAwesomeAPI,
    CurrencyItem,
    CurrencyType,
    CurrencyList,
    DatabaseCurrencyList,
)
from typing import Type, List


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
    updated_currencies = get_last_updated_document(track_coll)
    del updated_currencies["_id"]
    db_currency_list_obj = DatabaseCurrencyList(**updated_currencies)

    rate_coll.insert_one(db_currency_list_obj.model_dump())
    real_currencies_list = db_currency_list_obj.get_currencies_list()

    url = api.url_builder(real_currencies_list)

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
    database_currency_list_obj = DatabaseCurrencyList(currencies=default_currencies)
    tracked_collection.insert_one(database_currency_list_obj.model_dump())


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
