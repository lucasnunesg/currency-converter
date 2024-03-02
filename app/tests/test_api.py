import random
import string

import requests


def test_health_check():
    response = requests.get("http://0.0.0.0:8000/")
    assert response.status_code == 200


def test_economia_awesome_ap_health_check():
    response = requests.get("http://economia.awesomeapi.com.br/json/last/USD-BRL")
    assert response.status_code == 200


def test_available_currencies():
    response = requests.get("http://0.0.0.0:8000/v1/available-currencies/")
    assert response.status_code == 200


def test_rates_usd():
    response = requests.get("http://0.0.0.0:8000/v1/available-currencies/")
    assert response.status_code == 200
    assert type(response.json()) == list


def test_conversion_same_currency():
    amount = random.uniform(1, 1000)
    response = requests.get(
        f"http://localhost:8000/v1/conversion?source_currency=USD&target_currency=USD&amount={amount}")
    assert response.json() == amount


def test_add_custom_currency():
    code = "ABCDEFG123321HIJ"
    rate = 10
    response = requests.post(f"http://0.0.0.0:8000/v1/add-custom-currency?code={code}&rate_usd={rate}")
    assert "ABCDEFG123321HIJ" in response.json()


def test_track_real_currency():
    code = "XAGG"
    response = requests.post(f"http://0.0.0.0:8000/v1/track-real-currency?code={code}")
    assert code in response.json()


def test_delete_currency():
    response1 = requests.delete("http://0.0.0.0:8000/v1/delete-currency?code=ABCDEFG123321HIJ")
    response2 = requests.delete("http://0.0.0.0:8000/v1/delete-currency?code=XAGG")
    assert response1.status_code == 200
    assert response2.status_code == 200


def test_conversion():
    code1 = ''.join(random.choices(string.ascii_letters + string.digits, k=10)).upper()
    code2 = ''.join(random.choices(string.ascii_letters + string.digits, k=10)).upper()
    rate1 = random.uniform(1, 1000)
    rate2 = random.uniform(1, 1000)
    amount = random.uniform(1, 1000)

    r1 = requests.post(f'http://0.0.0.0:8000/v1/add-custom-currency?code={code1}&rate_usd={rate1}')
    r2 = requests.post(f'http://0.0.0.0:8000/v1/add-custom-currency?code={code2}&rate_usd={rate2}')

    response = requests.get(f'http://0.0.0.0:8000/v1/conversion?source_currency={code1}&target_currency={code2}&amount={amount}')

    result = amount * rate1 / rate2

    assert int(response.json()*1000) == int(result*1000)
