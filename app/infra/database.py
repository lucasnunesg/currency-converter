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
    currency_list: list = DEFAULT_CURRENCIES,
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
    db = mongodb_connect()
    update_conversion_collection(db=db)
