from datetime import datetime
from typing import Type

from fastapi import Depends
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session

from app.api.v2.external_api import CurrencyApiInterface, EconomiaAwesomeAPI
from app.api.v2.models import Currency, CurrencyType
from app.api.v2.schemas import CurrencySchema
from app.pg_database import get_session
from app.settings import Settings


def update_conversion(session: Session, api: CurrencyApiInterface = EconomiaAwesomeAPI) -> None:
    """Updates conversion for real currencies."""
    currencies_list = []

    rows = session.query(Currency).filter(Currency.type == CurrencyType.REAL).all()
    for row in rows:
        if row.type == CurrencyType.REAL:
            currencies_list.append(row.code)
    url = api.url_builder(currencies_list)
    updated_usd_rate_dict = api.get_conversion(url=url)

    for row in rows:
        code = row.code
        if code in updated_usd_rate_dict:
            row.rate_usd = updated_usd_rate_dict[code]
            session.commit()
            session.refresh(row)



