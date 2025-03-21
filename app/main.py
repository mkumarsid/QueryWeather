import logging
from fastapi import FastAPI
from app.api.routes import router
from app.core.config import db, shutdown_db

app = FastAPI(title="Weather Metrics API", version="1.0")

from pathlib import Path

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

csv_path = Path(__file__).resolve().parent.parent / "data" / "dublin_last_5_days_hourly_with_station_new.csv"
app.include_router(router)

@app.on_event("startup")
def startup():
    # Insert CSV only once at startup
    logger.info("Starting up the Weather Metrics API...")
    print("🚀 Loading initial CSV data into DuckDB...")
    #db.insert_csv("data/dublin_last_5_days_hourly_with_station.csv")
    try:
        db.insert_csv(str(csv_path))
        logger.info("CSV data successfully ingested into DuckDB.")
    except Exception as e:
        logger.error(f"Error during CSV ingestion: {e}")
    
@app.on_event("shutdown")
def shutdown():
    logger.info("Shutting down the Weather Metrics API...")
    shutdown_db()