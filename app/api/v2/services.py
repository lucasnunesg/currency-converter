from datetime import datetime, timedelta
from typing import Type

import pytz
from fastapi import Depends
from sqlalchemy import select, create_engine, desc
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
            row.update_time = datetime.now().astimezone(pytz.utc)
            session.commit()
            session.refresh(row)


def check_if_update(session: Session):
    """Checks if the current data is updated."""
    rows = session.query(Currency).filter(Currency.type == CurrencyType.REAL).order_by(desc(Currency.update_time))
    oldest_update = rows.first().update_time
    if oldest_update.replace(tzinfo=pytz.utc) < datetime.now().astimezone(pytz.utc) - timedelta(seconds=30):
        return True
    return False


def get_usd_rate(session: Session, code: str) -> float:
    """Returns usd rate of given currency."""
    return session.query(Currency).filter(Currency.code == code).first().rate_usd


def check_currency_exists_db(session: Session, code: str) -> bool:
    """Check if currency already exists in database."""
    result = session.query(Currency).filter(Currency.code == code).first()
    if result:
        return True
    return False

