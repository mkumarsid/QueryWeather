# 🌤️ QueryWeather

A modern weather monitoring system built using **FastAPI**, **Streamlit**, and **DuckDB**, wrapped in a lightweight **Dockerized** architecture.

> Real-time and historical weather metrics dashboard with interactive visualizations.

![Query Weather Platform](images/QueryWeatherDesign.png "Modern Data Stack!")

# Pre-requisites

- [Python 3.11](https://www.python.org/downloads/)
- [Open Weather API Key](https://home.openweathermap.org/api_keys)
- [Docker desktop](https://docs.docker.com/desktop/install/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)

# How to Run

1. Clone the Repo

```bash
git clone https://github.com/mkumarsid/QueryWeather.git
cd QueryWeather
```

2. Run with Docker (Recommended)

```bash
docker-compose up --build
docker-compose logs -f  # In separate terminal
```

3. Setup using Python Script (Cross-Platform)

4. Run this once to install Poetry, create a virtual environment, and install dependencies:

```bash
python setup_env.py


# Activate the environment
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows

# Run the app locally
poetry run python scripts/run_local.py
```

# Access Services

1. API - http://localhost:8000/docs

   ![FastAPI](images/fastapi.png "FastAPI")

2. Web UI (Streamlit App) - http://localhost:8501

   ![Streamlit App](images/streamlit.png "Streamlit App")
