import logging
import time

from fastapi import FastAPI, Request

from app.api.routes import router
from app.core.config import db, shutdown_db
from utils.logger_service import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Weather Metrics API", version="1.0")
from pathlib import Path

app.include_router(router)


@app.on_event("startup")
def startup():
    logger.info("Starting up the Weather Metrics API...")

    data_dir = Path(__file__).resolve().parent.parent / "data"
    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        logger.warning("No CSV files found in the data/ directory.")
        return

    for csv_file in csv_files:
        try:
            logger.info(f"Ingesting {csv_file.name} into DuckDB...")
            db.insert_csv(str(csv_file))
            logger.info(f"Successfully ingested: {csv_file.name}")
        except Exception as e:
            logger.error(f"Failed to ingest {csv_file.name}: {e}")


# Basic middleware for logging request processing time
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start) * 1000, 2)
    logging.info(f"{request.method} {request.url.path} - {process_time} ms")

    # Optional: Add header to response for access in Streamlit
    response.headers["X-Process-Time-ms"] = str(process_time)
    return response


@app.on_event("shutdown")
def shutdown():
    logger.info("Shutting down the Weather Metrics API...")
    shutdown_db()
