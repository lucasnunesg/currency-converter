import unittest
from datetime import datetime
from enum import Enum

import pytz

from app.api.v2.models import CurrencyType, Currency


class TestCurrencyType(unittest.TestCase):
    """Tests currency type class."""

    def test_is_enum(self):
        """Tests if class inherits from Enum."""
        self.assertTrue(issubclass(CurrencyType, Enum))

    def default_values(self):
        """Tests if default values include 'real' and 'backing'."""
        self.assertTrue(CurrencyType.REAL.value in CurrencyType.__members__.values())
        self.assertTrue(CurrencyType.BACKING.value in CurrencyType.__members__.values())


class TestCurrency(unittest.TestCase):
    """Tests currency database."""

    def test_attributes(self):
        """Tests attributes."""
        time = datetime.now().astimezone(pytz.utc)
        currency = Currency(code="TEST", rate_usd=2, type=CurrencyType.REAL, update_time=time)
        self.assertEqual(currency.code, "TEST")
        self.assertEqual(currency.rate_usd, 2)
        self.assertEqual(currency.type, CurrencyType.REAL)
        self.assertEqual(currency.update_time, time)
