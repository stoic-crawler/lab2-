from app.main import app
from random import randint
import pytest

x, y = randint(0, 1000), randint(0, 10000)
# Use Flask test client
client = app.test_client()

def test_add():
    response = client.get(f"/add?a={x}&b={y}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == x + y

def test_subtract():
    response = client.get(f"/subtract?a={x}&b={y}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == x - y

def test_multiply():
    response = client.get(f"/multiply?a={x}&b={y}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == x * y

while y == 0:  # ensure no division by zero
    y = randint(0, 10000)


def test_divide():
    response = client.get(f"/divide?a={x}&b={y}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == x / y

def test_divide_by_zero():
    response = client.get(f"/divide?a={x}&b=0")
    assert response.status_code == 400
    data = response.get_json()
    assert data["detail"] == "Division by zero"

