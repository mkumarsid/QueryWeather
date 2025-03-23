import streamlit as st
import requests
from datetime import date, timedelta
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Weather Metrics Dashboard", layout="wide")

# Helper Class
class WeatherAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch(self, endpoint, params=None):
        try:
            r = requests.get(f"{self.base_url}{endpoint}", params=params)
            if r.status_code == 200:
                return r.json(), r.headers
            else:
                st.error(f"Error {r.status_code}: {r.text}")
                return None, {}
        except Exception as e:
            st.error(f"❌ Request failed: {e}")
            return None, {}

    def compute_date_range(self, duration):
        end_date = date.today()
        if duration == "1 Week":
            start_date = end_date - timedelta(weeks=1)
        elif duration == "1 Month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=90)
        return start_date, end_date

class SensorDashboard:
    def __init__(self, api):
        self.api = api

    def render(self):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("🛰️ Sensor List (Latest Readings)")
        refresh = st.button("🔄 Resync from Live API")

        sensors, headers = ([], {})
        if refresh:
            with st.spinner("Refreshing sensors from live API..."):
                sensors, headers = self.api.fetch("/sensors")
                if sensors:
                    st.success("✅ Sensors resynced successfully from live API.")
        else:
            sensors, headers = self.api.fetch("/sensors")

        if "X-Process-Time-ms" in headers:
            col2.markdown(f"⏱️ {headers['X-Process-Time-ms']} ms")

        if sensors:
            st.dataframe(sensors)

class MetricExplorer:
    def __init__(self, api):
        self.api = api

    def render(self):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("📊 Metric Explorer")

        metrics = st.multiselect("Select Metrics", ["Temperature", "Humidity", "WindSpeed"], default=["Temperature"])
        duration = st.selectbox("Date Range", ["1 Week", "1 Month", "3 Months"])
        start_date, end_date = self.api.compute_date_range(duration)
        params = [("metrics", m) for m in metrics] + [("start_date", str(start_date)), ("end_date", str(end_date))]

        if st.button("📈 View Average"):
            data, headers = self.api.fetch("/metrics/average", params)
            if "X-Process-Time-ms" in headers:
                col2.markdown(f"⏱️ {headers['X-Process-Time-ms']} ms")
            if data:
                st.dataframe(data)

class MetricStats:
    def __init__(self, api):
        self.api = api

    def render(self):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("📉 Metric Statistics")

        metric = st.selectbox("Metric", ["Temperature", "Humidity", "WindSpeed"])
        stat = st.selectbox("Stat", ["avg", "min", "max", "sum"])
        duration = st.selectbox("Date Range", ["1 Week", "1 Month", "3 Months"], key="stats_duration")
        start_date, end_date = self.api.compute_date_range(duration)

        if st.button("📊 Compute Stats"):
            params = {
                "metric": metric,
                "stat": stat,
                "start_date": str(start_date),
                "end_date": str(end_date)
            }
            data, headers = self.api.fetch("/metrics/stat", params)
            if "X-Process-Time-ms" in headers:
                col2.markdown(f"⏱️ {headers['X-Process-Time-ms']} ms")
            if data:
                st.dataframe(data)

class HistoryViewer:
    def __init__(self, api):
        self.api = api

    def render(self):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("📜 Historical Data Viewer")

        metrics = st.multiselect("Select Metrics", ["Temperature", "Humidity", "WindSpeed"], default=["Temperature"])
        duration = st.selectbox("Date Range", ["1 Week", "1 Month", "3 Months"], key="history_duration")
        start_date, end_date = self.api.compute_date_range(duration)

        if st.button("📊 Fetch Historical Data"):
            params = [("metrics", m) for m in metrics] + [("start_date", str(start_date)), ("end_date", str(end_date))]
            data, headers = self.api.fetch("/metrics/data", params)
            if "X-Process-Time-ms" in headers:
                col2.markdown(f"⏱️ {headers['X-Process-Time-ms']} ms")
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)
                st.line_chart(df.set_index("Datetime")[metrics])

# App Router
api = WeatherAPI(API_URL)

st.sidebar.header("🌤️ WeatherBoard v1.0")
tab = st.sidebar.radio("🗂️ Explore Dashboard:", ["🛰️ Sensors", "📊 Metric Explorer", "📉 Metric Stats", "📜 History Viewer"])

if tab == "🛰️ Sensors":
    SensorDashboard(api).render()
elif tab == "📊 Metric Explorer":
    MetricExplorer(api).render()
elif tab == "📉 Metric Stats":
    MetricStats(api).render()
elif tab == "📜 History Viewer":
    HistoryViewer(api).render()
