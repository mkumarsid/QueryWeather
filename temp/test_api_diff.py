import requests
import pandas as pd
from datetime import datetime, timedelta
import os

GHCND_DATA_URL_BASE = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/"
STATION_ID = "ACW00011604"  # Correct GHCN-D station ID for Dublin Airport
DLY_FILENAME = f"{STATION_ID}.dly"
LOCAL_DLY_PATH = f"./{DLY_FILENAME}"

# NOAA GHCN-D supported daily elements of interest
ELEMENTS = {
    "TMAX": "Max Temperature (°C)",
    "TMIN": "Min Temperature (°C)",
    "AWND": "Average Wind Speed (m/s)"
}


def download_station_data():
    url = GHCND_DATA_URL_BASE + DLY_FILENAME
    print(f"Downloading data from {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(LOCAL_DLY_PATH, 'wb') as f:
            f.write(response.content)
        print("✅ Data downloaded successfully.")
    else:
        raise Exception(f"Failed to download data. Status code: {response.status_code}")


def parse_dly_file(filepath):
    records = []
    today = datetime.utcnow().date()
    date_30_days_ago = today - timedelta(days=30)

    with open(filepath, 'r') as file:
        for line in file:
            station = line[0:11].strip()
            year = line[11:15]
            month = line[15:17]
            element = line[17:21]
            if element not in ELEMENTS:
                continue
            for day in range(1, 32):
                value = line[21 + (day - 1) * 8:26 + (day - 1) * 8].strip()
                if value != "-9999":
                    date_str = f"{year}-{month.zfill(2)}-{str(day).zfill(2)}"
                    try:
                        date_obj = pd.to_datetime(date_str).date()
                        if date_30_days_ago <= date_obj <= today:
                            records.append((station, "Dublin Airport", date_str, element, int(value) / 10.0))
                    except ValueError:
                        continue

    df = pd.DataFrame(records, columns=["station", "location", "date", "element", "value"])
    df = df.pivot_table(index=["station", "location", "date"], columns="element", values="value").reset_index()
    df = df.rename(columns={"TMAX": "Max Temp (°C)", "TMIN": "Min Temp (°C)", "AWND": "Wind Speed (m/s)"})
    return df


if __name__ == "__main__":
    download_station_data()
    df = parse_dly_file(LOCAL_DLY_PATH)
    print("\n📊 Weather Data - Last 30 Days for Dublin:\n")
    print(df.head(30))
    os.remove(LOCAL_DLY_PATH)  # Optional cleanup
