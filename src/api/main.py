from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

# Initialize FastAPI app
app = FastAPI(
    title="Weather Sensor API",
    description="API for receiving and querying weather sensor data.",
    version="1.0.0"
)

# In-memory storage for sensor data
sensor_data = []

# Sensor data model
class SensorData(BaseModel):
    sensor_id: str
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None

# API to receive new sensor data
@app.post("/sensor-data", summary="Receive new sensor data")
def receive_sensor_data(data: SensorData):
    sensor_data.append(data.dict())
    return {"message": "Sensor data received successfully"}

# API to query sensor data
@app.get("/query", summary="Query sensor data")
def query_sensor_data(
    sensors: Optional[List[str]] = Query(None, description="List of sensor IDs"),
    metrics: List[str] = Query(..., description="Metrics to retrieve (e.g., temperature, humidity)"),
    statistic: str = Query(..., description="Statistic to compute: min, max, sum, average"),
    start_date: Optional[datetime] = Query(None, description="Start date (defaults to 7 days ago)"),
    end_date: Optional[datetime] = Query(None, description="End date (defaults to now)")
):
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()

    filtered_data = [entry for entry in sensor_data if start_date <= entry["timestamp"] <= end_date and (sensors is None or entry["sensor_id"] in sensors)]
    
    if not filtered_data:
        raise HTTPException(status_code=404, detail="No data found for the given criteria")
    
    results = {}
    for metric in metrics:
        values = [entry[metric] for entry in filtered_data if metric in entry and entry[metric] is not None]
        if not values:
            continue
        if statistic == "min":
            results[metric] = min(values)
        elif statistic == "max":
            results[metric] = max(values)
        elif statistic == "sum":
            results[metric] = sum(values)
        elif statistic == "average":
            results[metric] = sum(values) / len(values)
        else:
            raise HTTPException(status_code=400, detail="Invalid statistic type")
    
    return {"query_results": results}

# Root endpoint
@app.get("/", summary="Home", description="API root endpoint.")
def home():
    return {"message": "Welcome to the Weather Sensor API"}

# Run with: uvicorn filename:app --reload