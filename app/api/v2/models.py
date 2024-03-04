from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CurrencyType(Enum):

    """Currency types: real or created by user."""
    REAL = "real"
    CUSTOM = "custom"
    BACKING = "backing"


class Base(DeclarativeBase):
    pass


class Currency(Base):

    """Currency model"""
    __tablename__ = "currencies"

    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    code: Mapped[str]
    rate_usd: Mapped[float]
    type: Mapped[CurrencyType]
    update_time: Mapped[datetime]

