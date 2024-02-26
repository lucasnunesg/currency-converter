import json

from fastapi import APIRouter
from app.infra.database import DEFAULT_CURRENCIES

router = APIRouter(prefix="/v1", tags=["V1"])


@router.get("/")
def convert(from_currency: str, to_currency: str, amount: float):
    return {"rom": f"{from_currency}", "to": f"{to_currency}", "amount": f"{amount}"}


@router.get("/available-currencies")
def get_available_currencies():
    return DEFAULT_CURRENCIES
