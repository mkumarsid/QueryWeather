from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from weather_duckdb_utils import WeatherDB, WeatherMetric

app = FastAPI(title="Weather Metrics API", version="1.0")

db = WeatherDB()

class MetricQuery(BaseModel):
    metrics: List[str] = Field(..., example=["Temperature", "Humidity"])
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class StatQuery(BaseModel):
    metric: str = Field(..., example="Temperature")
    stat: str = Field(..., example="avg")
    start_date: Optional[date] = None
    end_date: Optional[date] = None

@app.get("/sensors")
def get_sensors(station_ids: Optional[List[str]] = Query(default=None)):
    """Get unique sensor/station details"""
    return db.get_sensor_details(station_ids).to_dict(orient="records")

@app.post("/metrics/average")
def get_average_metrics(query: MetricQuery):
    """Get average values for selected metrics in optional date range"""
    return db.get_metrics_average(query.metrics, query.start_date, query.end_date).to_dict(orient="records")

@app.post("/metrics/stat")
def get_metric_stat(query: StatQuery):
    """Get statistic (min, max, sum, avg) for a specific metric"""
    return db.get_metric_stats(query.metric, query.stat, query.start_date, query.end_date).to_dict(orient="records")

@app.post("/metrics")
def post_weather_metric(metric: WeatherMetric):
    """Post a new weather metric entry"""
    db.insert_metrics(metric)
    return {"status": "success", "message": "Metric inserted"}

@app.on_event("shutdown")
def shutdown():
    db.close()
