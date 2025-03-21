from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
#from app.db.duckdb_utils import WeatherDB, WeatherMetric

from app.db.duck_db_utils import WeatherDB, WeatherMetric

router = APIRouter()
db = WeatherDB()

class MetricQuery(BaseModel):
    metrics: List[str]
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class StatQuery(BaseModel):
    metric: str
    stat: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None

@router.get("/sensors")
def get_sensors(station_ids: Optional[List[str]] = Query(default=None)):
    return db.get_sensor_details(station_ids).to_dict(orient="records")

@router.post("/metrics/average")
def get_average_metrics(query: MetricQuery):
    return db.get_metrics_average(query.metrics, query.start_date, query.end_date).to_dict(orient="records")

@router.post("/metrics/stat")
def get_metric_stat(query: StatQuery):
    return db.get_metric_stats(query.metric, query.stat, query.start_date, query.end_date).to_dict(orient="records")

@router.post("/metrics")
def post_weather_metric(metric: WeatherMetric):
    db.insert_metrics(metric)
    return {"status": "success", "message": "Metric inserted"}