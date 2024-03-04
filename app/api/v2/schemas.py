from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.api.v2.models import CurrencyType


class CurrencySchema(BaseModel):
    """pydantic schema to expose Currency model to documentation"""
    code: str
    rate_usd: float
    type: CurrencyType
    model_config = ConfigDict(from_attributes=True)


class CurrencyDB(CurrencySchema):
    """pydantic schema to store currencies in database"""
    id: int
    update_time: datetime


class CurrencyList(BaseModel):
    currencies: list[CurrencySchema]