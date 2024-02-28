from fastapi import APIRouter
import json

from api.v1.models import CurrencyItemListResponse, CurrencyItem, CurrencyList
from app.database import (
    get_last_updated_document,
    init_databases,
    get_cursor_remove_fields,
)

router = APIRouter(prefix="/v1", tags=["V1"])

rate_coll, tracked_coll = init_databases()


@router.get("/")
def convert(from_currency: str, to_currency: str, amount: float):
    return {"from": f"{from_currency}", "to": f"{to_currency}", "amount": f"{amount}"}


@router.get("/available-currencies", response_model=CurrencyItemListResponse)
def get_available_currencies():
    """Testar o response_model, resgatar o último documento, fazer o parse com o modelo criando um objeto currencyList e depois retorna-lo como currencylistresponse"""

    all_documents_no_id = get_cursor_remove_fields(tracked_coll, ["_id"])
    currency_item_list = [CurrencyItem.model_validate(i) for i in all_documents_no_id]
    currency_list = CurrencyList(currency_item_list)
    """
    last_doc = get_last_updated_document(tracked_coll)
    del last_doc["_id"]
    currency_obj = CurrencyItem(**last_doc)
    return [currency_obj]
    """
    return currency_list


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
