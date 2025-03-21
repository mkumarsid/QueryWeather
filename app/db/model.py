from pydantic import BaseModel
from datetime import datetime

class WeatherMetric(BaseModel):
    station_id: str
    city: str
    country: str
    Datetime: datetime
    Temperature: float
    Humidity: int
    WindSpeed: float
    WeatherDescription: str