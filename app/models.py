from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MetricStatRequest(BaseModel):
    metrics: List[str] = Field(..., example=["Temperature", "Humidity"])
    stat: str = Field(..., example="avg")
    start_date: Optional[date] = Field(None, example="2025-03-18")
    end_date: Optional[date] = Field(None, example="2025-03-21")
    city: Optional[str] = Field(None, example="Dublin")


class MetricStatResponse(BaseModel):
    station_id: str
    city: str
    country: str
    avg_Temperature: Optional[float] = None
    avg_Humidity: Optional[float] = None
    avg_WindSpeed: Optional[float] = None


class SensorQuery(BaseModel):
    station_ids: Optional[List[str]] = Field(
        default=None, example=["DUBLIN_53.33_-6.25"]
    )


class WeatherMetric(BaseModel):
    station_id: str
    city: str
    country: str
    Datetime: datetime
    Temperature: float
    Humidity: int
    WindSpeed: float
    WeatherDescription: str
