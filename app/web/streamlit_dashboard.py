from datetime import date, timedelta

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

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
        self._cache_key = "sensor_data"

    def render(self):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("🛰️ Sensor List (Latest & Forecast Readings)")

        refresh = st.button("🔄 Resync from Live API")

        # Optional filter in future: station_ids = [...]
        payload = {"station_ids": None}

        if refresh or self._cache_key not in st.session_state:
            with st.spinner("Fetching sensor data..."):
                try:
                    response = requests.post(
                        f"{self.api.base_url}/sensors", json=payload
                    )
                    if response.status_code == 200:
                        sensors = response.json()
                        headers = response.headers
                        st.session_state[self._cache_key] = (sensors, headers)
                        if refresh:
                            st.success("✅ Sensors refreshed.")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                        sensors, headers = [], {}
                except Exception as e:
                    st.error(f"❌ Failed to load sensors: {e}")
                    sensors, headers = [], {}
        else:
            sensors, headers = st.session_state[self._cache_key]

        if "X-Process-Time-ms" in headers:
            col2.markdown(f"⏱️ {headers['X-Process-Time-ms']} ms")

        if sensors:
            df = pd.DataFrame(sensors)
            st.dataframe(df)

            try:
                city_coords = {"Dublin": [53.33, -6.25], "Galway": [53.27, -9.05]}
                m = folium.Map(location=[53.3, -8.5], zoom_start=6)

                for _, row in df.iterrows():
                    city = row.get("city")
                    coords = city_coords.get(city)
                    if coords:
                        tooltip = row["station_id"]
                        popup = f"{city}<br>🌡️ {row.get('Temperature', '?')} °C<br>💧 {row.get('Humidity', '?')} %"
                        folium.Marker(
                            location=coords, tooltip=tooltip, popup=popup
                        ).add_to(m)

                st.markdown("### 🗺️ Sensor Locations")
                st_folium(m, width=700, height=400)
            except Exception as e:
                st.warning(f"Map rendering failed: {e}")

class MetricStats:
    def __init__(self, api):
        self.api = api
        self._cache_key = "metric_stats"

    def render(self):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("📉 Metric Statistics")

        metrics = st.multiselect(
            "Select Metrics",
            ["Temperature", "Humidity", "WindSpeed"],
            default=["Temperature"],
        )
        stat = st.selectbox("Select Stat", ["avg", "min", "max", "sum"])
        city = st.selectbox("Select City", ["All", "Dublin", "Galway"])

        duration = st.selectbox(
            "Date Range", ["1 Week", "1 Month", "3 Months"], key="stats_duration"
        )
        end_date = date.today()
        if duration == "1 Week":
            start_date = end_date - timedelta(days=7)
        elif duration == "1 Month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=90)

        custom = st.checkbox("Custom Date Range", key="custom_stats")
        if custom:
            start_date = st.date_input("Start Date", start_date)
            end_date = st.date_input("End Date", end_date)

        should_fetch = (
            st.button("📊 Compute Stats") or self._cache_key not in st.session_state
        )

        if should_fetch:
            with st.spinner("Computing stats..."):
                payload = {
                    "metrics": metrics,
                    "stat": stat,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                }
                if city != "All":
                    payload["city"] = city

                try:
                    response = requests.post(
                        f"{self.api.base_url}/metrics/stat", json=payload
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state[self._cache_key] = (data, response.headers)
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                        st.session_state[self._cache_key] = ([], {})
                except Exception as e:
                    st.error(f"Request failed: {e}")
                    st.session_state[self._cache_key] = ([], {})

        data, headers = st.session_state.get(self._cache_key, ([], {}))
        if "X-Process-Time-ms" in headers:
            col2.markdown(f"⏱️ {headers['X-Process-Time-ms']} ms")

        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)

# App Router
api = WeatherAPI(API_URL)

st.sidebar.header("🌤️ WeatherBoard v1.0")
tab = st.sidebar.radio(
    "🗂️ Explore Dashboard:",
    [
        "🛰️ Sensors",
        "📉 Metric Stats",
    ],
)

if tab == "🛰️ Sensors":
    SensorDashboard(api).render()
elif tab == "📉 Metric Stats":
    MetricStats(api).render()
