from fastapi.testclient import TestClient
from app.main import app
#client = TestClient(app)

import httpx
import unittest
import requests


def response_type():
    response = requests.get("http://0.0.0.0:8000/docs/")
    status_code = response.status_code
    assert status_code == 200


"""def test_root():
    with httpx.Client() as client:
        response = client.get("0.0.0:8000/")
        assert response.status_code == 200"""


"""def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Server is running!"
    pass


def test_available_currencies():
    response = client.get("/available-currencies")
    assert response.status_code == 200
    pass
"""