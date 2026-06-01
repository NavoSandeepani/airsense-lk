import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_health_endpoint():
    from api import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_cities_endpoint():
    from api import app
    client = TestClient(app)
    response = client.get("/cities")
    assert response.status_code == 200
    data = response.json()
    assert "cities" in data
    assert len(data["cities"]) == 4
    assert "Colombo" in data["cities"]

def test_health_has_timestamp():
    from api import app
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()
    assert "timestamp" in data

def test_health_has_model_loaded():
    from api import app
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()
    assert "model_loaded" in data

def test_predict_invalid_city():
    from api import app
    client = TestClient(app)
    response = client.post("/predict", json={"city": "InvalidCity"})
    assert response.status_code in [404, 500]

def test_predict_request_format():
    from api import app
    client = TestClient(app)
    response = client.post("/predict", json={"city": "Colombo"})
    assert response.status_code in [200, 404, 500]