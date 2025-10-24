from app.main import app
from random import randint
import pytest

# Flask test client
client = app.test_client()

# API token for authentication
HEADERS = {"Authorization": "Bearer secret123"}

# Random numbers for tests
x = randint(0, 1000)
y = randint(1, 10000)  # ensure y != 0 to avoid division by zero

def test_add():
    response = client.get(f"/add?a={x}&b={y}", headers=HEADERS)
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == x + y

def test_subtract():
    response = client.get(f"/subtract?a={x}&b={y}", headers=HEADERS)
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == x - y

def test_multiply():
    response = client.get(f"/multiply?a={x}&b={y}", headers=HEADERS)
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == x * y

def test_divide():
    response = client.get(f"/divide?a={x}&b={y}", headers=HEADERS)
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == x / y

def test_divide_by_zero():
    response = client.get(f"/divide?a={x}&b=0", headers=HEADERS)
    assert response.status_code == 400
    data = response.get_json()
    assert data["detail"] == "Division by zero"

def test_invalid_numeric():
    # Test invalid input
    response = client.get(f"/add?a=foo&b=bar", headers=HEADERS)
    assert response.status_code == 400
    data = response.get_json()
    assert data["detail"] == "Invalid numeric input"

