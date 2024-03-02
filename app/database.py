from typing import Type, List

from pymongo import MongoClient
from pymongo.collection import Collection

from app.api.v1.models import (
    CurrencyApiInterface,
    EconomiaAwesomeAPI,
    CurrencyItem,
    CurrencyType,
    CurrencyList,
    DatabaseCurrencyList,
)


def mongodb_connect(
        database: str = "database",
        collection: str = "collection",
        host: str = "database",
        port: int = 27017,
) -> Collection:
    """Returns a pymongo collection connected to MongoDB.

    Arguments:
        database (str): database name.
        collection (str): collection name.
        host (str): Host address of the MongoDB server.
        port (int): Port number.

    Returns:
        Collection (pymongo.collection.Collection): MongoDB collection.
    """

    client = MongoClient(host=host, port=port)

    database = client[f"{database}"]

    collection = database[f"{collection}"]

    return collection


def get_last_updated_document(collection: Collection) -> dict:
    """Returns the last document added to a given collection."""
    return collection.find_one({}, sort=[("_id", -1)])


def update_conversion_collection(
        usd_rate_collection: Collection,
        tracked_collection: Collection,
        api: Type[CurrencyApiInterface] = EconomiaAwesomeAPI,
) -> None:
    """Updates the conversions (relative to USD value) using the external API.

    Takes all registered currencies on tracked_collection and creates a new document in
    usd_rate_coll with updated currency conversion values (in relation to USD value) based on the provided API instance.

    Arguments:
        usd_rate_collection (Collection): pymongo collection of the currency rates.
        tracked_collection (Collection): pymongo collection of the currency list (will be used to fetch all
                registered currencies).
        api (CurrencyApiInterface): API class (must be a valid CurrencyAPI subclass) to fetch external data.
    """
    updated_currencies = get_last_updated_document(tracked_collection)
    del updated_currencies["_id"]
    db_currency_list_obj = DatabaseCurrencyList(**updated_currencies)

    usd_rate_collection.insert_one(db_currency_list_obj.model_dump())
    real_currencies_list = db_currency_list_obj.get_currencies_list()

    url = api.url_builder(real_currencies_list)

    api.get_conversion(url, usd_rate_collection, tracked_collection)

    last_two_documents = usd_rate_collection.find().sort([("_id", -1)]).limit(2)

    last_two_documents_list = list(last_two_documents)
    penultimate_document = last_two_documents_list[1].get("_id")
    usd_rate_collection.delete_one({"_id": penultimate_document})


def check_empty_collection(collection: Collection) -> bool:
    """Checks if a given collection is empty (document count == 0)."""
    if collection.count_documents({}) == 0:
        return True
    return False


def populate_tracked_currencies(tracked_collection: Collection) -> None:
    """Populates de tracked currencies database based on the default list: BRL, EUR, BTC, ETH, USD."""
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
    """Initialize Rate and Tracked Currencies databases with default currencies."""
    rate_collection = mongodb_connect(database="database", collection="currency_rate")
    tracked_collection = mongodb_connect(
        database="database", collection="tracked_currencies"
    )
    if check_empty_collection(tracked_collection):
        populate_tracked_currencies(tracked_collection)
    return [rate_collection, tracked_collection]


# instantiating both collections.
[currency_rate_collection, tracked_currencies_collection] = init_databases()

# updating conversion rates.
update_conversion_collection(
    usd_rate_collection=currency_rate_collection,
    tracked_collection=tracked_currencies_collection,
    api=EconomiaAwesomeAPI)
