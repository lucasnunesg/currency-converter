from http.client import HTTPResponse

from fastapi import APIRouter

from app.api.v1.services import (
    fetch_all_currencies,
    fetch_external_api,
    fetch_all_currency_rates,
    get_conversion_service,
    add_custom_currency_service, track_real_currency_service,
)

router = APIRouter(prefix="/v1", tags=["V1"])


@router.get("/")
def hello():
    return "Welcome to Currency Conversion API"


@router.get("/available-currencies")
def get_available_currencies():
    return fetch_all_currencies()


@router.get("/rates-usd")
def get_rates():
    """Gets conversion rates from all currencies in relation to USD"""
    return fetch_all_currency_rates()


@router.get("/conversion")
def get_conversion(source_currency: str, target_currency: str, amount: float):
    conversion = get_conversion_service(source_currency, target_currency)
    return conversion * amount


@router.post("/track-real-currency")
def track_real_currency(code: str):
    track_real_currency_service(code)
    return f"Currency wih {code=} successfully added"


@router.post("/add-custom-currency")
def add_custom_currency(code: str, rate_usd: float):
    add_custom_currency_service(code, rate_usd)
    fetch_external_api()
    return "Currency added successfully"
