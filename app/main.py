from fastapi import FastAPI
from app.api.routes import router
from app.core.config import db, shutdown_db

app = FastAPI(title="Weather Metrics API", version="1.0")

from pathlib import Path



csv_path = Path(__file__).resolve().parent.parent / "data" / "dublin_last_5_days_hourly_with_station_new.csv"
app.include_router(router)

@app.on_event("startup")
def startup():
    # Insert CSV only once at startup
    print("🚀 Loading initial CSV data into DuckDB...")
    #db.insert_csv("data/dublin_last_5_days_hourly_with_station.csv")
    db.insert_csv(str(csv_path))
    
@app.on_event("shutdown")
def shutdown():
    shutdown_db()