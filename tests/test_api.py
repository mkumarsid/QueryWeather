# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_post_sensors_empty():
    response = client.post("/sensors", json={})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_post_metrics_stat_valid():
    payload = {
        "metrics": ["Temperature", "Humidity"],
        "stat": "avg",
        "start_date": "2025-03-01",
        "end_date": "2025-03-07",
        "city": "Dublin"
    }
    response = client.post("/metrics/stat", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_post_metrics_stat_invalid_metric_triggers_400():
    payload = {
        "metrics": ["Rainfall"],  # Invalid
        "stat": "avg"
    }
    response = client.post("/metrics/stat", json=payload)
    #print("Response text:", response.text)
    assert response.status_code == 400

def test_post_metrics_stat_triggers_500():
    """Trigger 500 by sending unsupported stat"""
    payload = {
        "metrics": ["Temperature"],
        "stat": "median"  # not in ['avg', 'min', 'max', 'sum']
    }
    response = client.post("/metrics/stat", json=payload)
    print("500 test response:", response.text)
    assert response.status_code == 500
    assert "Internal Server Error" in response.text
