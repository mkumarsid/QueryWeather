# run_local.py
# Utility script to run FastAPI weather app locally

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "weather_api_app:app",
        host="127.0.0.1",
        port=8000,
        reload=True  # enables auto-reload for development
    )