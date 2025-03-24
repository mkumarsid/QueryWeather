# 🌤️ QueryWeather

A modern weather monitoring system built using **FastAPI**, **Streamlit**, and **DuckDB**, wrapped in a lightweight **Dockerized** architecture.

> Real-time and historical weather metrics dashboard with interactive visualizations.

---

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

## ⚙️ Local Setup (with Poetry)

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/your-username/QueryWeather.git
cd QueryWeather

```
