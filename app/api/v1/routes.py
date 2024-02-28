from fastapi import APIRouter
import json

from api.v1.models import CurrencyItemListResponse, CurrencyItem, CurrencyList
from database import (
    get_last_updated_document,
    init_databases,
    get_cursor_remove_fields,
    test_func,
)

router = APIRouter(prefix="/v1", tags=["V1"])

[currency_rate_collection, tracked_currencies_collection] = init_databases()


@router.get("/")
def convert(from_currency: str, to_currency: str, amount: float):
    return {"from": f"{from_currency}", "to": f"{to_currency}", "amount": f"{amount}"}


@router.get("/available-currencies", response_model=CurrencyItemListResponse)
def get_available_currencies():
    """Testar o response_model, resgatar o último documento, fazer o parse com o modelo criando um objeto
    currencyList e depois retorna-lo como currencylistresponse"""

    """all_documents_no_id = get_cursor_remove_fields(
        tracked_currencies_collection, ["_id"]
    )
    currency_item_list = [CurrencyItem.model_validate(i) for i in all_documents_no_id]
    currency_list = CurrencyList(currency_item_list)"""

    return test_func()


"""
@router.get("/rates")
def get_rates():
    doc = get_cursor_remove_fields(rate_coll, fields=["_id", "update_time"])
    list_docs = list(doc)
    only_currencies = [doc.get("currencies") for doc in list_docs]
    for item in only_currencies:
        for i in item:
            i.pop("_id")
        # item[0].pop("_id")
    return only_currencies
"""
