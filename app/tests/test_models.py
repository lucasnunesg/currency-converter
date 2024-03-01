import unittest
from abc import ABC
from datetime import datetime, timedelta
from enum import Enum
from unittest.mock import MagicMock, patch


import pytz

from app.api.v1.models import (
    CurrencyItem,
    CurrencyList,
    CurrencyApiInterface,
    EconomiaAwesomeAPI,
    CurrencyType,
    DatabaseCurrencyList,
)


class TestCurrencyType(unittest.TestCase):
    def test_is_enum(self):
        self.assertTrue(issubclass(CurrencyType, Enum))

    def default_values(self):
        self.assertTrue(CurrencyType.REAL.value in CurrencyType.__members__.values())
        self.assertTrue(CurrencyType.BACKING.value in CurrencyType.__members__.values())


class TestCurrencyItem(unittest.TestCase):
    """Test CurrencyItem class"""

    def test_currency_item(self):
        """
        Test if CurrencyItem instance is created properly
        """
        currency_item = CurrencyItem(code="USD", rate_usd=1.0, currency_type="real")
        self.assertEqual(currency_item.code, "USD")
        self.assertEqual(currency_item.rate_usd, 1.0)
        self.assertEqual(currency_item.currency_type, "real")


class TestCurrencyList(unittest.TestCase):
    """
    Test CurrencyList class
    """

    def test_currency_list(self):
        """
        Test if CurrencyList instance is created properly
        """
        currency_item_1 = CurrencyItem(code="USD", rate_usd=1.0, currency_type="real")
        currency_item_2 = CurrencyItem(code="EUR", rate_usd=0.9, currency_type="custom")
        currency_list = CurrencyList(
            list_of_currencies=[currency_item_1, currency_item_2]
        )
        self.assertEqual(len(currency_list.list_of_currencies), 2)

    def test_get_currency_list(self):
        """
        Test get_currency_list method
        """
        currency_item_1 = CurrencyItem(code="USD", rate_usd=1.0, currency_type="real")
        currency_item_2 = CurrencyItem(code="EUR", rate_usd=0.9, currency_type="custom")
        currency_list = CurrencyList(
            list_of_currencies=[currency_item_1, currency_item_2]
        )
        self.assertEqual(currency_list.get_currency_list(), ["USD", "EUR"])

    def test_list_currency_items(self):
        """
        Test list_currency_items method
        """
        currency_item_1 = CurrencyItem(code="USD", rate_usd=1.0, currency_type="real")
        currency_item_2 = CurrencyItem(code="EUR", rate_usd=0.9, currency_type="custom")
        currency_list = CurrencyList(
            list_of_currencies=[currency_item_1, currency_item_2]
        )
        self.assertEqual(len(currency_list.list_currency_items()), 2)

    def test_get_real_currencies(self):
        """
        Test get_real_currencies method
        """
        currency_list = CurrencyList(
            [
                CurrencyItem(code="USD", rate_usd=1.0, currency_type="backing"),
                CurrencyItem(code="EUR", rate_usd=1.55, currency_type="real"),
                CurrencyItem(code="ABC", rate_usd=2, currency_type="custom"),
            ]
        )
        self.assertEqual(
            currency_list.get_real_currencies(),
            CurrencyList(
                [CurrencyItem(code="EUR", rate_usd=1.55, currency_type="real")]
            ),
        )

    def test_get_currency_rate(self):
        currency_list = CurrencyList(
            [
                CurrencyItem(code="USD", rate_usd=1.0, currency_type="backing"),
                CurrencyItem(code="EUR", rate_usd=1.55, currency_type="real"),
                CurrencyItem(code="ABC", rate_usd=2, currency_type="custom"),
            ]
        )
        self.assertEqual(
            currency_list.get_currency_rate(), {"USD": 1.0, "EUR": 1.55, "ABC": 2}
        )


class TestDatabaseCurrencyList(unittest.TestCase):
    """Tests for DatabaseCurrencyList"""

    def test_database_currency_list(self):
        """
        Test if DatabaseCurrencyList instance is created properly
        """
        currency_list = CurrencyList(
            [
                CurrencyItem(code="USD", rate_usd=1.0, currency_type="backing"),
                CurrencyItem(code="EUR", rate_usd=1.55, currency_type="real"),
                CurrencyItem(code="ABC", rate_usd=2, currency_type="custom"),
            ]
        )
        db_currency_list = DatabaseCurrencyList(currencies=currency_list)
        self.assertTrue(hasattr(db_currency_list, "currencies"))
        self.assertTrue(hasattr(db_currency_list, "update_time"))

    def test_update_timestamp(self):
        """
        Test update_timestamp method
        """
        currency_list = CurrencyList(
            [
                CurrencyItem(code="USD", rate_usd=1.0, currency_type="backing"),
                CurrencyItem(code="EUR", rate_usd=1.55, currency_type="real"),
                CurrencyItem(code="ABC", rate_usd=2, currency_type="custom"),
            ]
        )
        db_currency_list = DatabaseCurrencyList(currencies=currency_list)
        db_currency_list.update_timestamp()
        diff = datetime.now().astimezone(pytz.utc) - db_currency_list.update_time
        self.assertTrue(diff < timedelta(milliseconds=0.1))

    def test_return_currency_list_obj(self):
        currency_list = CurrencyList(
            [
                CurrencyItem(code="USD", rate_usd=1.0, currency_type="backing"),
                CurrencyItem(code="EUR", rate_usd=1.55, currency_type="real"),
                CurrencyItem(code="ABC", rate_usd=2, currency_type="custom"),
            ]
        )
        db_currency_list = DatabaseCurrencyList(currencies=currency_list)
        currency_list_obj = db_currency_list.currencies.model_dump().get(
            "list_of_currencies"
        )
        self.assertEqual(
            currency_list_obj,
            [
                {"code": "USD", "rate_usd": 1.0, "currency_type": "backing"},
                {"code": "EUR", "rate_usd": 1.55, "currency_type": "real"},
                {"code": "ABC", "rate_usd": 2.0, "currency_type": "custom"},
            ],
        )

    def test_get_currencies_list(self):
        currency_list = CurrencyList(
            [
                CurrencyItem(code="USD", rate_usd=1.0, currency_type="backing"),
                CurrencyItem(code="EUR", rate_usd=1.55, currency_type="real"),
                CurrencyItem(code="ABC", rate_usd=2, currency_type="custom"),
            ]
        )
        db_currency_list = DatabaseCurrencyList(currencies=currency_list)
        self.assertEqual(
            db_currency_list.currencies.model_dump().get("list_of_currencies"),
            [
                {"code": "USD", "currency_type": "backing", "rate_usd": 1.0},
                {"code": "EUR", "currency_type": "real", "rate_usd": 1.55},
                {"code": "ABC", "currency_type": "custom", "rate_usd": 2.0},
            ],
        )


class TestCurrencyApiInterface(unittest.TestCase):
    """Test CurrencyApiInterface class"""

    def test_abstract_methods(self):
        """Test if abstract methods are implemented properly"""
        # Checks if the class is abstract
        self.assertTrue(issubclass(CurrencyApiInterface, ABC))

        # Checks if the abstract methods are implemented
        self.assertTrue(
            hasattr(EconomiaAwesomeAPI, "url_builder")
            and callable(EconomiaAwesomeAPI.url_builder)
        )
        self.assertTrue(
            hasattr(EconomiaAwesomeAPI, "get_conversion")
            and callable(EconomiaAwesomeAPI.get_conversion)
        )


class TestEconomiaAwesomeAPI(unittest.TestCase):
    """Test EconomiaAwesomeAPI class"""

    @patch("requests.get")
    def test_get_conversion(self, mock_get):
        """Test get_conversion method"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "USD": {"code": "USD", "bid": 5.0},
            "EUR": {"code": "EUR", "bid": 4.0},
        }
        mock_get.return_value = mock_response

        rate_coll = MagicMock()
        track_coll = MagicMock()
        EconomiaAwesomeAPI.get_conversion("url", rate_coll, track_coll)
