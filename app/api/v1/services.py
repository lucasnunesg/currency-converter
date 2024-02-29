from datetime import datetime, timedelta

import pytz

from api.v1.models import CurrencyType, DatabaseCurrencyList
from database import (
    tracked_currencies_collection,
    currency_rate_collection,
    get_last_updated_document,
    update_conversion_collection,
)


def fetch_all_currencies() -> dict:
    last_doc = get_last_updated_document(tracked_currencies_collection)
    del last_doc["_id"]
    obj = DatabaseCurrencyList(**last_doc)
    return obj.get_currencies_list(all_currencies=True)


def fetch_all_currency_rates() -> list:
    last_doc = get_last_updated_document(currency_rate_collection)
    del last_doc["_id"]
    only_currencies = last_doc.get("currencies")
    no_id_list = [i for i in only_currencies if i != "_id"]
    for i in no_id_list:
        i.pop("_id")
    return no_id_list


def fetch_external_api() -> None:
    update_conversion_collection(
        currency_rate_collection, tracked_currencies_collection
    )
    return None


def fetch_conversion(source_currency: str, target_currency: str) -> float:
    if source_currency.upper() == target_currency.upper():
        return 1
    last_doc = get_last_updated_document(currency_rate_collection)
    del last_doc["_id"]
    obj = DatabaseCurrencyList(**last_doc)
    if obj.update_time < datetime.now().astimezone(pytz.utc) - timedelta(minutes=2):
        fetch_external_api()
    cl = obj.return_currency_list_obj()
    dic = cl.get_currency_rate()

    def find_usd_rate(currency: str):
        if currency == "USD":
            return 1
        else:
            return dic.get(currency)

    if target_currency.upper() == "USD":
        return find_usd_rate(source_currency)
    else:
        return find_usd_rate(source_currency) / find_usd_rate(target_currency)


def add_tracked_currency(code: str, rate_usd: float) -> None:
    """Adds a new currency provided by the user to the collection"""
    updated_currencies = get_last_updated_document(tracked_currencies_collection)
    del updated_currencies["_id"]
    db_currency_list_obj = DatabaseCurrencyList(**updated_currencies)
    dic = db_currency_list_obj.model_dump()
    new_currency = {
        "code": code,
        "currency_type": CurrencyType.CUSTOM.value,
        "rate_usd": rate_usd,
    }
    updated_currencies.get("currencies").get("list_of_currencies").append(new_currency)

    tracked_currencies_collection.insert_one(updated_currencies)
