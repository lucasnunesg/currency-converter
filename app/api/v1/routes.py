import json

from fastapi import APIRouter
from app.infra.database import currencies

router = APIRouter(prefix="/v1", tags=["V1"])


@router.get("/")
def convert(from_currency: str, to_currency: str, amount: float):
    return {"from": f"{from_currency}", "to": f"{to_currency}", "amount": f"{amount}"}


@router.get("/available-currencies")
def get_available_currencies():
    return currencies
