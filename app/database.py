from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from pymongo.cursor import Cursor

from api.v1.models import (
    CurrencyApiInterface,
    EconomiaAwesomeAPI,
    CurrencyItem,
    CurrencyType,
    CurrencyList,
)
from typing import Type, List
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


def from_tracked_to_rate(tracked_coll: Collection, rate_coll: Collection) -> None:
    """Updates currencies of rate_coll based on all documents inside tracked_coll"""
    all_documents_no_id = get_cursor_remove_fields(tracked_coll, ["_id"])
    currency_item_list = [CurrencyItem.model_validate(i) for i in all_documents_no_id]
    currency_list = CurrencyList(currency_item_list)
    rate_coll.insert_one(currency_list.to_tracked_currencies_model())


def add_tracked_currency(
    code: str, rate_usd: float, collection: Collection
) -> Collection:
    """Adds a new currency provided by the user to the collection"""
    collection.insert_one(
        CurrencyItem(
            code=code, rate_usd=rate_usd, currency_type=CurrencyType.CUSTOM.value
        ).dict()
    )
    return collection


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

    from_tracked_to_rate(track_coll, rate_coll)
    currency_list_object = parse_last_rate_document_to_object(rate_coll)
    real_currency_objects = currency_list_object.get_real_currencies()
    currency_list = real_currency_objects.get_currency_list()
    url = api.url_builder(currency_list)

    api.get_conversion(url, rate_coll, track_coll)

    last_two_documents = rate_coll.find().sort([("_id", -1)]).limit(2)

    last_two_documents_list = list(last_two_documents)
    penultimate_document = last_two_documents_list[1].get("_id")
    rate_coll.delete_one({"_id": penultimate_document})


def parse_last_rate_document_to_object(rate_coll: Collection) -> CurrencyList:
    """Converts the last document from a given collection into a CurrencyList object"""
    dic = get_last_updated_document(rate_coll)
    del dic["_id"]
    currency_list = CurrencyList(dic.get("currencies"))

    return currency_list


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


if __name__ == "__main__":
    [currency_rate_collection, tracked_currencies_collection] = init_databases()

    update_conversion_collection(
        rate_coll=currency_rate_collection,
        track_coll=tracked_currencies_collection,
        api=EconomiaAwesomeAPI,
    )
