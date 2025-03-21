import streamlit as st
import requests
from datetime import date

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Weather API Dashboard", layout="wide")
st.title("🌦️ Weather Metrics Dashboard")

st.sidebar.header("Query Options")

# Select endpoint
tab = st.sidebar.radio("Choose Endpoint", ["Sensors", "Average Metrics", "Metric Stats"])

if tab == "Sensors":
    st.subheader("🔍 Sensor List (with Latest Readings and Date)")
    response = requests.get(f"{API_URL}/sensors")
    if response.status_code == 200:
        sensors = response.json()
        st.dataframe(sensors)  # This will now include Temperature, Humidity, WindSpeed
    else:
        st.error("Failed to fetch sensor data")

elif tab == "Average Metrics":
    st.subheader("📊 Average Metrics Query")
    metrics = st.multiselect("Select Metrics", ["Temperature", "Humidity", "WindSpeed"], default=["Temperature"])
    start_date = st.date_input("Start Date", date.today())
    end_date = st.date_input("End Date", date.today())

    if st.button("Get Averages"):
        params = [("metrics", m) for m in metrics]
        params += [("start_date", str(start_date)), ("end_date", str(end_date))]
        response = requests.get(f"{API_URL}/metrics/average", params=params)
        if response.status_code == 200:
            st.dataframe(response.json())
        else:
            st.error(response.text)

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
