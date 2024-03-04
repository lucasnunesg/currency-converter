from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v2.models import Currency, CurrencyType
from app.api.v2.schemas import CurrencyList, CurrencySchema
from app.pg_database import get_session
from app.api.v2.external_api import EconomiaAwesomeAPI, CurrencyApiInterface
from app.api.v2.services import update_conversion

router = APIRouter(prefix="/v2", tags=["V2 - Postgres"])

local_database = []
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


@router.post("/currencies/", response_model=CurrencySchema, status_code=201)
def create_currency(currency: CurrencySchema, session: Session = Depends(get_session)):
    db_currency = session.scalar(select(Currency).where(Currency.code == currency.code))

    if db_currency:
        raise HTTPException(status_code=404, detail="Currency already registered")

    db_currency = Currency(code=currency.code, rate_usd=currency.rate_usd, type=currency.type, update_time=datetime.now())
    session.add(db_currency)
    session.commit()
    session.refresh(db_currency)

    return db_currency


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
    """
    # session: Session = Depends(get_session)
    ...


@router.post("/track-real-currency", status_code=201)
def track_real_currency(code: str):
    """Adds real currencies to tracked list.

    Attributes:
          code (str): code of the real currency to be tracked.
    """
    ...


@router.post("/add-custom-currency", status_code=201)
def add_custom_currency(code: str, rate_usd: float):
    """Adds custom currency to tracked list with rate provided by the user.

    Attributes:
        code (str): code of the currency to be added.
        rate_usd (float): conversion rate related to USD value.
    """
    ...


@router.delete("/delete-currency", status_code=200)
def delete_currency(code: str):
    """Deletes currency based on its code."""
    ...


@router.put("/update-custom-currency", status_code=200)
def update_custom_currency_rate(code: str, usd_rate: float):
    """Updates custom currency usd_rate."""
    ...
