import streamlit as st
import requests
from datetime import date
from datetime import date, timedelta
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Weather API Dashboard", layout="wide")
st.title("🌦️ Weather Metrics Dashboard")

st.sidebar.header("Query Options")

# Select endpoint
tab = st.sidebar.radio("Choose Endpoint", ["Sensors", "Average Metrics", "Metric Stats"])


# if tab == "Sensors":
#     st.subheader("🔍 Sensor List (with Latest Readings and Date)")

#     if st.button("🔄 Resync Sensors"):
#         st.info("Fetching live forecast and refreshing sensor data...")

#     # Always trigger fresh request (resync or initial load)
#     response = requests.get(f"{API_URL}/sensors")

#     if response.status_code == 200:
#         sensors = response.json()
#         st.dataframe(sensors)
#     else:
#         st.error("Failed to fetch sensor data.")

#     # Show process time if available
#     if "X-Process-Time-ms" in response.headers:
#         st.info(f"⏱️ API Response Time: {response.headers['X-Process-Time-ms']} ms")

from datetime import datetime

from datetime import datetime

if tab == "Sensors":
    st.subheader("🔍 Sensor List (with Latest Readings and Date)")

    if "resync_triggered" not in st.session_state:
        st.session_state.resync_triggered = False
    if "last_synced" not in st.session_state:
        st.session_state.last_synced = None
    if "sensor_data" not in st.session_state:
        st.session_state.sensor_data = None
    if "last_api_time" not in st.session_state:
        st.session_state.last_api_time = None

    # Button to resync
    if st.button("🔄 Resync Sensors"):
        st.session_state.resync_triggered = True

    # Handle resync
    if st.session_state.resync_triggered:
        with st.spinner("🔄 Syncing data from OpenWeatherMap..."):
            response = requests.get(f"{API_URL}/sensors")
            if response.status_code == 200:
                st.session_state.sensor_data = response.json()
                st.session_state.last_synced = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.last_api_time = response.headers.get("X-Process-Time-ms", None)
                st.success("✅ Sensors resynced successfully from live API.")
            else:
                st.error("❌ Failed to sync data.")
            st.session_state.resync_triggered = False  # Reset trigger
    else:
        # Initial load
        if st.session_state.sensor_data is None:
            with st.spinner("📡 Loading sensor data..."):
                response = requests.get(f"{API_URL}/sensors")
                if response.status_code == 200:
                    st.session_state.sensor_data = response.json()
                    st.session_state.last_synced = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.last_api_time = response.headers.get("X-Process-Time-ms", None)
                else:
                    st.error("❌ Failed to load sensors.")

    # Display sensors
    if st.session_state.sensor_data:
        st.dataframe(st.session_state.sensor_data)

    # Info
    if st.session_state.last_synced:
        st.caption(f"🕒 Last Synced: {st.session_state.last_synced}")
    if st.session_state.last_api_time:
        st.caption(f"⏱️ API Response Time: {st.session_state.last_api_time} ms")


# if tab == "Sensors":
#     st.subheader("🔍 Sensor List (with Latest Readings and Date)")
#     response = requests.get(f"{API_URL}/sensors")
#     if response.status_code == 200:
#         sensors = response.json()
#         st.dataframe(sensors)  # This will now include Temperature, Humidity, WindSpeed
#     else:
#         st.error("Failed to fetch sensor data")
    
#     # Show process time if available
#     if "X-Process-Time-ms" in response.headers:
#         st.info(f"⏱️ API Response Time: {response.headers['X-Process-Time-ms']} ms")

elif tab == "Average Metrics":
    sub_tab = st.radio("Select Metric View:", ["📈 Average View", "📊 Historical Data"], horizontal=True)

    metrics = st.multiselect("Select Metrics", ["Temperature", "Humidity", "WindSpeed"], default=["Temperature"])
    # start_date = st.date_input("Start Date", date.today() - timedelta(days=7))
    # end_date = st.date_input("End Date", date.today())
    
    from datetime import timedelta

    duration = st.selectbox("Choose Date Range", ["1 Week", "1 Month", "3 Months"])
    end_date = date.today()

    if duration == "1 Week":
        start_date = end_date - timedelta(weeks=1)
    elif duration == "1 Month":
        start_date = end_date - timedelta(days=30)
    else:  # "3 Months"
        start_date = end_date - timedelta(days=90)


    if sub_tab == "📈 Average View":
        if st.button("Fetch Average Metrics"):
            params = [("metrics", m) for m in metrics]
            params += [("start_date", str(start_date)), ("end_date", str(end_date))]
            r = requests.get(f"{API_URL}/metrics/average", params=params)
            if r.status_code == 200:
                st.dataframe(r.json())
            else:
                st.error(r.text)
            
                # Show process time if available
            if "X-Process-Time-ms" in r.headers:
                st.info(f"⏱️ API Response Time: {r.headers['X-Process-Time-ms']} ms")

    elif sub_tab == "📊 Historical Data":
        if st.button("Fetch Historical Data"):
            params = [("metrics", m) for m in metrics]
            params += [("start_date", str(start_date)), ("end_date", str(end_date))]
            r = requests.get(f"{API_URL}/metrics/data", params=params)
            if r.status_code == 200:
                df = pd.DataFrame(r.json())
                st.dataframe(df)
                st.line_chart(df.set_index("Datetime")[metrics])
            else:
                st.error(r.text)
                
                            # Show process time if available
            if "X-Process-Time-ms" in r.headers:
                st.info(f"⏱️ API Response Time: {r.headers['X-Process-Time-ms']} ms")


elif tab == "Metric Stats":
    st.subheader("📈 Metric Statistics Query")
    metric = st.selectbox("Select Metric", ["Temperature", "Humidity", "WindSpeed"])
    stat = st.selectbox("Statistic", ["avg", "min", "max", "sum"])
    start_date = st.date_input("Start Date", date.today())
    end_date = st.date_input("End Date", date.today())

    if st.button("Get Stats"):
        params = {
            "metric": metric,
            "stat": stat,
            "start_date": str(start_date),
            "end_date": str(end_date)
        }
        response = requests.get(f"{API_URL}/metrics/stat", params=params)
        if response.status_code == 200:
            st.dataframe(response.json())
        else:
            st.error(response.text)
            
                        # Show process time if available
        if "X-Process-Time-ms" in response.headers:
            st.info(f"⏱️ API Response Time: {response.headers['X-Process-Time-ms']} ms")
