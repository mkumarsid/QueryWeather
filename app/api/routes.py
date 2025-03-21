
import logging
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from app.db.duck_db_utils import WeatherDB, WeatherMetric
from fastapi import APIRouter, Query, HTTPException, Body



# Configure logging: set level, format, and optionally file handler
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = APIRouter()
db = WeatherDB()
from pydantic import BaseModel, Field
# Allowed metrics in your DuckDB schema
ALLOWED_METRICS = {"Temperature", "Humidity", "WindSpeed"}

class MetricQuery(BaseModel):
    metrics: List[str] = Field(example=["Temperature", "Humidity"])
    start_date: Optional[date] = Field(example="2025-03-20")
    end_date: Optional[date] = Field(example="2025-03-21")

class StatQuery(BaseModel):
    metric: str = Field(example="Temperature")
    stat: str = Field(example="max")
    start_date: Optional[date] = Field(example="2025-03-18")
    end_date: Optional[date] = Field(example="2025-03-21")
    
# @router.get("/sensors")
# def get_sensors(station_ids: Optional[List[str]] = Query(default=None)):
#     return db.get_sensor_details(station_ids).to_dict(orient="records")

@router.get("/sensors")
def get_sensors(station_ids: Optional[List[str]] = Query(default=None)):
    return db.get_sensor_details(station_ids).to_dict(orient="records")

# @router.get("/metrics/average")
# def get_average_metrics(query: MetricQuery):
#     try:
#         print("📥 /metrics/average request:", query)
#         for metric in query.metrics:
#             if metric not in ALLOWED_METRICS:
#                 raise HTTPException(status_code=400, detail=f"Invalid metric '{metric}'. Allowed: {ALLOWED_METRICS}")
#         result = db.get_metrics_average(query.metrics, query.start_date, query.end_date)
#         return result.to_dict(orient="records")
#     except Exception as e:
#         print("❌ Error in /metrics/average:", str(e))
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/metrics/average")
def get_average_metrics(
    metrics: List[str] = Query(..., example=["Temperature", "Humidity"]),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    try:
        for metric in metrics:
            if metric not in ALLOWED_METRICS:
                raise HTTPException(status_code=400, detail=f"Invalid metric '{metric}'. Allowed: {ALLOWED_METRICS}")
        result = db.get_metrics_average(metrics, start_date, end_date)
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/metrics/stat")
def get_metric_stat(
    metric: str = Query(..., example="Temperature"),
    stat: str = Query(..., example="max"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    try:
        if metric not in ALLOWED_METRICS:
            raise HTTPException(status_code=400, detail=f"Invalid metric '{metric}'. Allowed: {ALLOWED_METRICS}")
        result = db.get_metric_stats(metric, stat, start_date, end_date)
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# @router.get("/metrics/stat")
# #def get_metric_stat(query: StatQuery):
# def get_metric_stat(
#     metric: str = Query(..., example="Temperature"),
#     stat: str = Query(..., example="max"),
#     start_date: Optional[date] = Query(None),
#     end_date: Optional[date] = Query(None)
# ):
#     try:
#         print("📥 /metrics/stat request:", query)
#         if query.metric not in ALLOWED_METRICS:
#             raise HTTPException(status_code=400, detail=f"Invalid metric '{query.metric}'. Allowed: {ALLOWED_METRICS}")
#         result = db.get_metric_stats(query.metric, query.stat, query.start_date, query.end_date)
#         return result.to_dict(orient="records")
#     except Exception as e:
#         print("❌ Error in /metrics/stat:", str(e))
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/metrics")
def post_weather_metric(metric: WeatherMetric):
    try:
        db.insert_metrics(metric)
        return {"status": "success", "message": "Metric inserted"}
    except Exception as e:
        print("❌ Error in /metrics:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
