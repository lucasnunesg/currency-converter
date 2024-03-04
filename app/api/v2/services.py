from datetime import datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v2.external_api import CurrencyApiInterface, EconomiaAwesomeAPI
from app.api.v2.models import Currency, CurrencyType
from app.api.v2.schemas import CurrencySchema
from app.pg_database import get_session


def update_currency_rates(currencies_list: list, api: CurrencyApiInterface = EconomiaAwesomeAPI) -> None:
    """Updates the currencies rate of the given database"""
    url = api.url_builder(currencies_list)
    currencies_usd_rate_dict = api.get_conversion(url=url)

    # Update the rates in the database




