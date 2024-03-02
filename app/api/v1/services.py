from datetime import datetime, timedelta

import httpx
import pytz
from fastapi import HTTPException, requests

from app.api.v1.models import CurrencyType, DatabaseCurrencyList
from app.database import (
    tracked_currencies_collection,
    currency_rate_collection,
    get_last_updated_document,
    update_conversion_collection,
)


def get_available_currencies_service() -> list:
    last_doc = get_last_updated_document(tracked_currencies_collection)
    del last_doc["_id"]
    obj = DatabaseCurrencyList(**last_doc)
    return obj.get_currencies_list(all_currencies=True)


def update_rates_service() -> list:
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


def get_conversion_service(source_currency: str, target_currency: str) -> float:
    if source_currency.upper() == target_currency.upper():
        return 1
    last_doc = get_last_updated_document(currency_rate_collection)
    del last_doc["_id"]
    obj = DatabaseCurrencyList(**last_doc)

    if source_currency not in obj.get_currencies_list(all_currencies=True):
        raise HTTPException(status_code=400, detail=f"Currency with code={source_currency} is not being tracked")
    if target_currency not in obj.get_currencies_list(all_currencies=True):
        raise HTTPException(status_code=400, detail=f"Currency with code={target_currency} is not being tracked")
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


def add_custom_currency_service(code: str, rate_usd: float) -> None:
    """Adds a new currency provided by the user to the collection"""
    updated_currencies = get_last_updated_document(tracked_currencies_collection)
    del updated_currencies["_id"]
    db_currency_list_obj = DatabaseCurrencyList(**updated_currencies)
    new_currency = {
        "code": code,
        "currency_type": CurrencyType.CUSTOM.value,
        "rate_usd": rate_usd,
    }
    currency_list = updated_currencies.get("currencies").get("list_of_currencies")
    if code.upper() in db_currency_list_obj.get_currencies_list():
        raise HTTPException(status_code=400, detail=f"Currency with {code=} is already being tracked")
    elif httpx.get(f"https://economia.awesomeapi.com.br/last/USD-{code}").status_code == 200:
        raise HTTPException(status_code=400, detail=f"Currency with {code=} already exists, please choose another "
                                                    f"code or add the real currency to the tracking list using the "
                                                    f"'track-real-currency' endpoint")
    else:
        currency_list.append(new_currency)

    tracked_currencies_collection.insert_one(updated_currencies)


def track_real_currency_service(code: str) -> None:
    request = httpx.get(f"https://economia.awesomeapi.com.br/last/{code}-USD")
    code = code.upper()
    updated_currencies = get_last_updated_document(tracked_currencies_collection)
    del updated_currencies["_id"]
    db_currency_list_obj = DatabaseCurrencyList(**updated_currencies)
    if request.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Currency with {code=} not found. Use 'add-custom-currency' to "
                            f"create and track it.")
    elif code.upper() in db_currency_list_obj.get_currencies_list(all_currencies=True):
        raise HTTPException(status_code=400, detail=f"Currency with {code=} is already being tracked")

    new_currency = {
        "code": code,
        "currency_type": CurrencyType.REAL.value,
        "rate_usd": 0,
    }
    currency_list = updated_currencies.get("currencies").get("list_of_currencies")
    currency_list.append(new_currency)
    tracked_currencies_collection.insert_one(updated_currencies)
    fetch_external_api()


def delete_currency_service(code: str):

    updated_currencies = get_last_updated_document(tracked_currencies_collection)
    del updated_currencies["_id"]
    db_currency_list_obj = DatabaseCurrencyList(**updated_currencies)
    if code not in db_currency_list_obj.get_currencies_list(all_currencies=True):
        raise HTTPException(status_code=400, detail=f"Currency with {code=} is not being tracked")

    currency_list = updated_currencies.get("currencies").get("list_of_currencies")
    for i in currency_list:
        if i.get("code") == code:
            del currency_list[currency_list.index(i)]
            break
    tracked_currencies_collection.insert_one(updated_currencies)
    fetch_external_api()

