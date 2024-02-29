from typing import List

from fastapi import APIRouter

from api.v1.models import CurrencyListResponse, CurrencyItemResponse
from api.v1.services import (
    fetch_all_currencies,
    fetch_external_api,
    fetch_all_currency_rates,
    fetch_conversion,
    add_tracked_currency,
)
from database import update_conversion_collection

# from database import init_databases
router = APIRouter(prefix="/v1", tags=["V1"])

# [currency_rate_collection, tracked_currencies_collection] = init_databases()


@router.get("/")
def convert(from_currency: str, to_currency: str, amount: float):
    return {"from": f"{from_currency}", "to": f"{to_currency}", "amount": f"{amount}"}


@router.get("/available-currencies", response_model=List[CurrencyItemResponse])
def get_available_currencies():
    return fetch_all_currencies()


@router.get("/rates-usd")
def get_rates():
    """Gets conversion rates from all currencies in relation to USD"""
    return fetch_all_currency_rates()


@router.get("/update-rates")
def update_rates():
    fetch_external_api()
    return "Conversion rates updated successfully"


@router.get("/conversion")
def get_conversion(source_currency: str, target_currency: str, amount: float):
    conversion = fetch_conversion(source_currency, target_currency)
    return conversion * amount


@router.post("/add-currency")
def add_currency(code: str, rate_usd: float):
    add_tracked_currency(code, rate_usd)
    fetch_external_api()
    return "Currency added successfully"
