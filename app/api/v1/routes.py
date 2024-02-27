import json

from fastapi import APIRouter
from database import get_list_of_currencies

router = APIRouter(prefix="/v1", tags=["V1"])


@router.get("/")
def convert(from_currency: str, to_currency: str, amount: float):
    return {"from": f"{from_currency}", "to": f"{to_currency}", "amount": f"{amount}"}


@router.get("/available-currencies")
def get_available_currencies():
    return get_list_of_currencies
