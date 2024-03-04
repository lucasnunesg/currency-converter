from datetime import datetime

import pytz
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v2.models import Currency, CurrencyType
from app.api.v2.schemas import CurrencyList, CurrencySchema
from app.api.v2.services import update_conversion, check_if_update, get_usd_rate, check_currency_exists_db
from app.pg_database import get_session

router = APIRouter(prefix="/v2", tags=["V2 - Postgres"])

currency_list = [
    CurrencySchema(code="BRL", rate_usd=0, type=CurrencyType.REAL),
    CurrencySchema(code="EUR", rate_usd=0, type=CurrencyType.REAL),
    CurrencySchema(code="BTC", rate_usd=0, type=CurrencyType.REAL),
    CurrencySchema(code="ETH", rate_usd=0, type=CurrencyType.REAL),
    CurrencySchema(code="USD", rate_usd=1, type=CurrencyType.REAL),
]


@router.get("/")
def populate_database(currencies: list[CurrencySchema] = currency_list, session: Session = Depends(get_session)):
    for currency in currencies:
        db_currency = session.scalar(select(Currency).where(Currency.code == currency.code))
        if not db_currency:
            db_currency = Currency(code=currency.code, rate_usd=currency.rate_usd, type=currency.type,
                                   update_time=datetime.now())
            session.add(db_currency)
            session.commit()
            session.refresh(db_currency)


@router.get("/available-currencies", response_model=CurrencyList)
def get_available_currencies(session: Session = Depends(get_session)):
    """Lists tracked currencies."""
    update_conversion(session=session)
    currencies = session.scalars(select(Currency)).all()
    return {"currencies": currencies}


@router.get("/conversion")
def get_conversion(source_currency: str, target_currency: str, amount: float, session: Session = Depends(get_session)):
    """Performs currency conversion.

    Attributes:
        source_currency (str): source currency code.
        target_currency (str): target currency code.
        amount (float): amount to convert.
        session (Session): db session (for dependency injection purposes).
    """
    if source_currency == target_currency:
        return {"result": "%.2f" % amount}

    if check_if_update(session=session):
        update_conversion(session=session)

    if target_currency == "USD":
        result = get_usd_rate(session=session, code=source_currency) * amount
        return {"result": "%.2f" % result}

    result = get_usd_rate(session, source_currency) / get_usd_rate(session, target_currency) * amount
    return {"result": "%.2f" % result}


@router.post("/track-real-currency", status_code=201, response_model=CurrencySchema)
def track_real_currency(code: str, session: Session = Depends(get_session)):
    """Adds real currencies to tracked list.

    Attributes:
          code (str): code of the real currency to be tracked.
    """
    code = code.upper()
    if check_currency_exists_db(code=code, session=session):
        raise HTTPException(status_code=400, detail=f"Currency with {code=} is already being tracked")
    response = requests.get(f"https://economia.awesomeapi.com.br/last/USD-{code}")
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Real currency with {code=} not found!")
    db_currency = Currency(code=code, rate_usd=0, type=CurrencyType.REAL,
                           update_time=datetime.now())
    session.add(db_currency)
    session.commit()
    session.refresh(db_currency)
    update_conversion(session=session)
    return db_currency


@router.post("/add-custom-currency", status_code=201, response_model=CurrencySchema)
def add_custom_currency(code: str, rate_usd: float, session: Session = Depends(get_session)):
    """Adds custom currency to tracked list with rate provided by the user.

    Attributes:
        code (str): code of the currency to be added.
        rate_usd (float): conversion rate related to USD value.
    """
    if check_currency_exists_db(code=code, session=session):
        raise HTTPException(status_code=404, detail=f"Currency with {code=} is already being tracked")
    response = requests.get(f"https://economia.awesomeapi.com.br/last/USD-{code}")
    if response.status_code == 200:
        raise HTTPException(status_code=400, detail=f"Real currency with {code=} already exists, please use another code")
    db_currency = Currency(code=code, rate_usd=rate_usd, type=CurrencyType.CUSTOM,
                           update_time=datetime.now().astimezone(pytz.utc))
    session.add(db_currency)
    session.commit()
    session.refresh(db_currency)
    return db_currency


@router.delete("/delete-currency", status_code=200)
def delete_currency(code: str, session: Session = Depends(get_session)):
    """Deletes currency based on its code."""
    currency = session.scalar(select(Currency).where(Currency.code == code))

    if not currency:
        raise HTTPException(status_code=404, detail=f"Currency with {code=} not found.")
    session.delete(currency)
    session.commit()
    return {"message": "Currency has been deleted successfully."}


@router.patch("/update-custom-currency", status_code=200, response_model=CurrencySchema)
def update_custom_currency_rate(code: str, rate_usd: float, session: Session = Depends(get_session)):
    """Updates custom currency usd_rate."""
    currency_db = session.scalar(select(Currency).where(Currency.code == code))
    if not currency_db:
        raise HTTPException(status_code=400, detail=f"Currency with {code=} not found.")
    delete_currency(code=code, session=session)
    return add_custom_currency(code=code, rate_usd=rate_usd, session=session)
