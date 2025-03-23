import logging
from fastapi import FastAPI
from app.api.routes import router
from app.core.config import db, shutdown_db

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource



trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "query-weather-api"})
    )
)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",  # if you're running Jaeger locally
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)



app = FastAPI(title="Weather Metrics API", version="1.0")
FastAPIInstrumentor.instrument_app(app)



from pathlib import Path

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

#csv_path = Path(__file__).resolve().parent.parent / "data" / "dublin_last_5_days_hourly_with_station_new.csv"
app.include_router(router)


import time
import logging
from fastapi import Request

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


@app.on_event("startup")
def startup():
    logger.info("Starting up the Weather Metrics API...")
    print("🚀 Scanning 'data/' folder for CSVs to load...")

    data_dir = Path(__file__).resolve().parent.parent / "data"
    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        logger.warning("⚠️ No CSV files found in the data/ directory.")
        return

    for csv_file in csv_files:
        try:
            logger.info(f"📥 Ingesting {csv_file.name} into DuckDB...")
            db.insert_csv(str(csv_file))
            logger.info(f"✅ Successfully ingested: {csv_file.name}")
        except Exception as e:
            logger.error(f"❌ Failed to ingest {csv_file.name}: {e}")
            
            
@app.on_event("shutdown")
def shutdown():
    logger.info("Shutting down the Weather Metrics API...")
    shutdown_db()