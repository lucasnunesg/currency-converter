import random
import string

import requests

from app.api.v1.models import DatabaseCurrencyList


def test_health_check():
    response = requests.get("http://0.0.0.0:8000/")
    assert response.status_code == 200


def test_economia_awesome_api_health_check():
    response = requests.get("http://economia.awesomeapi.com.br/json/last/USD-BRL")
    assert response.status_code == 200


def test_available_currencies():
    response = requests.get("http://0.0.0.0:8000/v1/available-currencies/")
    assert response.status_code == 200


def test_rates_usd():
    response = requests.get("http://0.0.0.0:8000/v1/available-currencies/")
    assert response.status_code == 200


def test_conversion_same_currency():
    amount = random.uniform(1, 1000)
    response = requests.get(
        f"http://localhost:8000/v1/conversion?source_currency=USD&target_currency=USD&amount={amount}")
    assert response.json() == {"result": amount}


def test_add_custom_currency():
    code = "ABCDEFG123321HIJ"
    rate = 10
    response = requests.post(f"http://0.0.0.0:8000/v1/add-custom-currency?code={code}&rate_usd={rate}")
    new_currency_dict = {"code": code, "currency_type": "custom", "rate_usd": rate}
    assert new_currency_dict in response.json()["currencies"]["list_of_currencies"]


def test_track_real_currency():
    code = "XAGG"
    response = requests.post(f"http://0.0.0.0:8000/v1/track-real-currency?code={code}")
    codes_list = [i.get("code") for i in response.json()["currencies"]["list_of_currencies"]]
    assert code in codes_list


def test_delete_currency():
    response1 = requests.delete("http://0.0.0.0:8000/v1/delete-currency?code=ABCDEFG123321HIJ")
    response2 = requests.delete("http://0.0.0.0:8000/v1/delete-currency?code=XAGG")
    obj = DatabaseCurrencyList(**response2.json())
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert "ABCDEFG123321HIJ" not in obj.get_currencies_list()
    assert "XAGG" not in obj.get_currencies_list()


def test_conversion():
    code1 = ''.join(random.choices(string.ascii_letters + string.digits, k=10)).upper()
    code2 = ''.join(random.choices(string.ascii_letters + string.digits, k=10)).upper()
    rate1 = random.uniform(1, 1000)
    rate2 = random.uniform(1, 1000)
    amount = random.uniform(1, 1000)

    requests.post(f'http://0.0.0.0:8000/v1/add-custom-currency?code={code1}&rate_usd={rate1}')
    requests.post(f'http://0.0.0.0:8000/v1/add-custom-currency?code={code2}&rate_usd={rate2}')

    response = requests.get(f'http://0.0.0.0:8000/v1/conversion?source_currency={code1}&target_currency={code2}&amount={amount}')

    result = amount * rate1 / rate2

    response_result = response.json().get("result")
    assert int(response_result*1000) == int(result*1000)
