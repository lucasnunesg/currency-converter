from datetime import datetime, timedelta

import httpx
import pytz
from fastapi import HTTPException

from app.api.v1.models import CurrencyType, DatabaseCurrencyList
from app.database import (
    tracked_currencies_collection,
    currency_rate_collection,
    get_last_updated_document,
    update_conversion_collection,
)


def get_available_currencies_service() -> DatabaseCurrencyList:
    """Lists tracked currencies."""
    fetch_external_api()
    delete_penultimate_document()
    last_doc = get_last_updated_document(currency_rate_collection)
    del last_doc["_id"]
    obj = DatabaseCurrencyList(**last_doc)
    return obj


def fetch_external_api() -> None:
    """Updates conversion rates."""
    update_conversion_collection(
        currency_rate_collection, tracked_currencies_collection
    )
    return None


def delete_penultimate_document() -> None:
    last_two_documents = currency_rate_collection.find().sort([("_id", -1)]).limit(2)

    last_two_documents_list = list(last_two_documents)
    penultimate_document = last_two_documents_list[1].get("_id")
    currency_rate_collection.delete_one({"_id": penultimate_document})


def get_conversion_service(source_currency: str, target_currency: str) -> float:
    """Performs currency conversion.

    Attributes:
    source_currency (str): source currency code.
    target_currency (str): target currency code.
    """
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
        delete_penultimate_document()
    cl = obj.return_currency_list_obj()
    dic = cl.get_currency_rate()

    def find_usd_rate(currency: str):
        """Returns single conversion rate based on USD value."""
        if currency == "USD":
            return 1
        else:
            return dic.get(currency)

    if target_currency.upper() == "USD":
        return find_usd_rate(source_currency)
    else:
        return find_usd_rate(source_currency) / find_usd_rate(target_currency)


def add_custom_currency_service(code: str, rate_usd: float) -> None:
    """Adds custom currency to tracked list with rate provided by the user.

    Attributes:
        code (str): code of the currency to be added.
        rate_usd (float): conversion rate related to USD value.
    """
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
    """Adds real currencies to tracked list.

    Attributes:
          code (str): code of the real currency to be tracked.
    """
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
    delete_penultimate_document()


def delete_currency_service(code: str):
    """Deletes currency based on its code."""
    updated_currencies = get_last_updated_document(currency_rate_collection)
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
    updated_currencies_obj = get_available_currencies_service()
    delete_penultimate_document()
    return updated_currencies_obj


def update_custom_currency_rate_service(code: str, usd_rate: float):
    """Updates custom currency usd_rate."""
    delete_currency_service(code)
    add_custom_currency_service(code, usd_rate)
    fetch_external_api()
    delete_penultimate_document()
    updated_currencies_obj = get_available_currencies_service()
    return updated_currencies_obj
