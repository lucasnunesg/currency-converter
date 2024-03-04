import unittest

from app.api.v2.models import CurrencyType
from app.api.v2.schemas import CurrencySchema, CurrencyList


class TestCurrencySchema(unittest.TestCase):
    """Tests CurrencySchema class."""

    def test_attributes(self):
        """Test attributes."""
        schema = CurrencySchema(code="TEST", rate_usd=4, type=CurrencyType.CUSTOM)
        self.assertEqual(schema.code, "TEST")
        self.assertEqual(schema.rate_usd, 4)
        self.assertEqual(schema.type, CurrencyType.CUSTOM)


class TestCurrencyList(unittest.TestCase):
    """Tests CurrencyList class."""

    def test_currencies_attribute(self):
        """Tests attributes."""
        currencies = [
            CurrencySchema(code='USD', rate_usd=1.0, type=CurrencyType.REAL),
            CurrencySchema(code='BRL', rate_usd=1.2, type=CurrencyType.REAL),
            CurrencySchema(code='EUR', rate_usd=1.4, type=CurrencyType.REAL)
        ]
        currency_list = CurrencyList(currencies=currencies)
        self.assertEqual(currency_list.currencies, currencies)

    def test_empty_currencies_attribute(self):
        """Tests empty currencies attribute."""
        currency_list = CurrencyList(currencies=[])
        self.assertEqual(currency_list.currencies, [])
