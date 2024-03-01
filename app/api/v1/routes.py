from fastapi import APIRouter

from app.api.v1.services import (
    get_available_currencies_service,
    fetch_external_api,
    update_rates_service,
    get_conversion_service,
    add_custom_currency_service, track_real_currency_service,
)

router = APIRouter(prefix="/v1", tags=["V1"])


@router.get("/")
def root():
    return "Welcome to Currency Conversion API"


@router.get("/available-currencies")
def get_available_currencies():
    """ Lists tracked currencies """
    return get_available_currencies_service()


@router.get("/rates-usd")
def update_rates():
    """Gets conversion rates from all currencies in relation to USD"""
    return update_rates_service()


@router.get("/conversion")
def get_conversion(source_currency: str, target_currency: str, amount: float):
    """ Performs currency conversion"""
    conversion = get_conversion_service(source_currency, target_currency)
    return conversion * amount


@router.post("/track-real-currency")
def track_real_currency(code: str):
    """Adds real currencies to tracked list"""
    track_real_currency_service(code)
    return {"details": f"Currency wih {code=} is now being tracked"}


@router.post("/add-custom-currency")
def add_custom_currency(code: str, rate_usd: float):
    """Adds custom currency to tracked list with rate provided by the user"""
    add_custom_currency_service(code, rate_usd)
    fetch_external_api()
    return {"details": f"Custom currency wih {code=} created successfully"}
