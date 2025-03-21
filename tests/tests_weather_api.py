import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# --- Sensor endpoint ---
def test_get_sensors():
    response = client.get("/sensors")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# --- Average metrics ---
def test_average_metrics():
    response = client.get("/metrics/average", params={
        "metrics": ["Temperature", "Humidity"],
        "start_date": "2025-03-20",
        "end_date": "2025-03-21"
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# --- Metric statistics ---
def test_metric_stats():
    response = client.get("/metrics/stat", params={
        "metric": "Temperature",
        "stat": "max",
        "start_date": "2025-03-18",
        "end_date": "2025-03-21"
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# --- Insert metric (basic smoke test) ---
def test_post_metric():
    payload = {
        "station_id": "DUBLIN_53.35_-6.26",
        "city": "Dublin",
        "country": "Ireland",
        "Datetime": "2025-03-21T12:00:00",
        "Temperature": 13.5,
        "Humidity": 75,
        "WindSpeed": 4.1,
        "WeatherDescription": "clear sky"
    }
    response = client.post("/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"