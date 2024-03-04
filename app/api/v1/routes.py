from fastapi import APIRouter, HTTPException

from app.api.v1.services import (
    get_available_currencies_service,
    fetch_external_api,
    get_conversion_service,
    add_custom_currency_service, track_real_currency_service, delete_currency_service,
    update_custom_currency_rate_service, delete_penultimate_document,
)
from app.api.v1.models import DatabaseCurrencyList, CurrencyItem, CurrencyList, ConversionResponse

router = APIRouter(prefix="/v1", tags=["V1"])


@router.get("/available-currencies", response_model=DatabaseCurrencyList)
def get_available_currencies():
    """Lists tracked currencies."""
    return get_available_currencies_service()


@router.get("/conversion", response_model=ConversionResponse)
def get_conversion(source_currency: str, target_currency: str, amount: float):
    """Performs currency conversion.
    
    Attributes:
        source_currency (str): source currency code.
        target_currency (str): target currency code.
        amount (float): amount to convert.
    """
    conversion = get_conversion_service(source_currency, target_currency)
    return {"result": conversion * amount}


@router.post("/track-real-currency", status_code=201, response_model=DatabaseCurrencyList)
def track_real_currency(code: str):
    """Adds real currencies to tracked list.
    
    Attributes:
          code (str): code of the real currency to be tracked.  
    """
    track_real_currency_service(code.upper())
    return get_available_currencies_service()


@router.post("/add-custom-currency", status_code=201, response_model=DatabaseCurrencyList)
def add_custom_currency(code: str, rate_usd: float):
    """Adds custom currency to tracked list with rate provided by the user.
    
    Attributes:
        code (str): code of the currency to be added.
        rate_usd (float): conversion rate related to USD value.
    """
    add_custom_currency_service(code.upper(), rate_usd)
    fetch_external_api()
    delete_penultimate_document()
    return get_available_currencies_service()


@router.delete("/delete-currency", status_code=200, response_model=DatabaseCurrencyList)
def delete_currency(code: str):
    """Deletes currency based on its code."""
    if code.upper() == "USD":
        raise HTTPException(status_code=404, detail="Can't delete backing currency.")

    return delete_currency_service(code.upper())


@router.put("/update-custom-currency", status_code=200, response_model=DatabaseCurrencyList)
def update_custom_currency_rate(code: str, usd_rate: float):
    """Updates custom currency usd_rate."""
    return update_custom_currency_rate_service(code, usd_rate)
