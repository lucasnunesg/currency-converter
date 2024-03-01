import requests


def test_health_check():
    response = requests.get("http://0.0.0.0:8000/docs/")
    status_code = response.status_code
    assert status_code == 200

