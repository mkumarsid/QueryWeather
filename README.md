# 🌤️ QueryWeather

A modern weather monitoring system built using **FastAPI**, **Streamlit**, and **DuckDB**, wrapped in a lightweight **Dockerized** architecture.

> Real-time and historical weather metrics dashboard with interactive visualizations.

## ![Query Weather](images/SystemDiagram.png "Query Weather")

## 🚀 Features

- 🛰️ Fetch live weather data via OpenWeatherMap API
- 📦 Store structured weather data in DuckDB (embedded)
- 🔍 Query metrics like temperature, humidity, windspeed (with stats & history)
- 📊 Visualize data via an interactive Streamlit dashboard
- 🐳 Dockerized for ease of deployment

---

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Database**: DuckDB
- **API Source**: OpenWeatherMap
- **Deployment**: Docker + Docker Compose
- **Packaging**: Poetry

---

## 🧱 Project Structure

QueryWeather/ ├── app/ # FastAPI backend ├── uinterface/ # Streamlit frontend ├── ingestion/ # Weather ingestion logic ├── data/ # CSV & database files ├── Dockerfile ├── docker-compose.yml ├── pyproject.toml

---

### ⚙️ Local Setup (with Poetry)

#### 1️⃣ Clone the Repo

```bash
git clone https://github.com/your-username/QueryWeather.git
cd QueryWeather
```

#### 2️⃣ Install Poetry

> Poetry is used for dependency and environment management.

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

If that doesn't work, see full docs: https://python-poetry.org/docs/#installation

#### 3️⃣ Install Dependencies

```bash
poetry install
```

#### 4️⃣ Activate Virtual Environment

```bash
poetry shell
```

#### 5️⃣ Run the App Locally

```bash
python scripts/run_local.py
```

You should now be able to access:

- ✅ FastAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📈 Streamlit Dashboard: [http://127.0.0.1:8501](http://127.0.0.1:8501)

---

### 🐳 Run with Docker (Recommended)

#### 1️⃣ Build and Run

```bash
docker-compose up --build
```

#### 2️⃣ Access Services

- 🚀 FastAPI Docs: http://localhost:8000/docs
- 📈 Streamlit UI: http://localhost:8501

---

### 🔑 API Configuration

This project pulls data from [OpenWeatherMap](https://openweathermap.org/api).

Update the `API_KEY` in:

```
ingestion/ingest_openweather.py
```

Or make it configurable via `.env` support if needed.

---

### 📁 Data Directory

- Your ingested/historical `.csv` files → stored in `data/`
- Local DuckDB database → `weather_data.db`

---

### ✅ TODOs

- [ ] Add CRON / Prefect job for scheduled ingestion
- [ ] Improve error logging for ingestion
- [ ] Push Docker image to GitHub Container Registry
- [ ] Add authentication for Streamlit

---

### 🤝 Contributing

Have suggestions or want to contribute? Feel free to fork and submit a pull request.

---
