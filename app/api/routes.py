from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel

from app.db.duck_db_utils import WeatherDB
from app.models import MetricStatRequest, SensorQuery, WeatherMetric

from utils.logger_service import get_logger
logger = get_logger(__name__)

# API Router class 
router = APIRouter()

# Duck DB connector class
db = WeatherDB()

@router.post("/sensors")
def get_sensors(payload: SensorQuery):
    logger.info(f"Fetching sensors for: {payload.station_ids}")
    return db.get_sensor_details(station_ids=payload.station_ids).to_dict(
        orient="records"
    )


@router.post("/metrics/stat")
def get_metric_stat(payload: MetricStatRequest):
    logger.info(f"Fetching {payload.stat} stats for: {payload.metrics}")
    
    for metric in payload.metrics:
        if metric not in {"Temperature", "Humidity", "WindSpeed"}:
            logger.warning(f"Invalid metric requested: {metric}")
            raise HTTPException(
            status_code=400, detail=f"Invalid metric '{metric}'"
            )
    try:

        results = []
        for metric in payload.metrics:
            df = db.get_metric_stats(
                metric=metric,
                stat=payload.stat,
                start_date=payload.start_date,
                end_date=payload.end_date,
                city=payload.city,
            )
            results.append(df)

        from pandas import concat

        combined = concat(results, axis=1)
        combined = combined.loc[:, ~combined.columns.duplicated()]
        return combined.to_dict(orient="records")

    except Exception as e:
        logger.exception("Unexpected error during /metrics/stat processing")
        raise HTTPException(status_code=500, detail="Internal Server Error")
