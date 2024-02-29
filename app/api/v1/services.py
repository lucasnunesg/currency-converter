from typing import List

from api.v1.models import CurrencyItem, CurrencyList, CurrencyType, DatabaseCurrencyList
from database import (
    get_cursor_remove_fields,
    tracked_currencies_collection,
    currency_rate_collection,
    get_last_updated_document,
    update_conversion_collection,
)


def fetch_all_currencies() -> dict:
    last_doc = get_last_updated_document(currency_rate_collection)
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
    if source_currency == target_currency:
        return 1

    def find_usd_rate(currency: str) -> float:
        last_doc = get_last_updated_document(currency_rate_collection)
        only_currencies = last_doc.get("currencies")
        no_id_list = [i for i in only_currencies if i != "_id"]
        for i in no_id_list:
            i.pop("_id")
        for i in no_id_list:
            if i.get("code").upper() == currency:
                return i.get("rate_usd")

    if target_currency.upper() == "USD":
        return float(find_usd_rate(source_currency))

    return float(find_usd_rate(source_currency)) / float(find_usd_rate(target_currency))


def add_tracked_currency(code: str, rate_usd: float) -> None:
    """Adds a new currency provided by the user to the collection"""
    tracked_currencies_collection.insert_one(
        CurrencyItem(
            code=code, rate_usd=rate_usd, currency_type=CurrencyType.CUSTOM.value
        ).dict()
    )
