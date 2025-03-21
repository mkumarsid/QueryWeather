import requests
import json
from datetime import datetime
import csv
import os

API_KEY = '5f416c6f2c4d94b658cb2be255c8c8c0'  # Replace with your OpenWeatherMap API key
CITY = 'Dublin'
CSV_LOG_PATH = 'owm_station_log.csv'


def fetch_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()


def extract_station_entry(data):
    timestamp = datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
    city = data['name']
    lat = data['coord']['lat']
    lon = data['coord']['lon']
    temp = data['main'].get('temp')
    humidity = data['main'].get('humidity')
    wind_speed = data['wind'].get('speed')

    station_id = f"{city}_{lat:.2f}_{lon:.2f}"

    return {
        "timestamp": timestamp,
        "station_id": station_id,
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "temperature (C)": temp,
        "humidity (%)": humidity,
        "wind speed (m/s)": wind_speed
    }


def log_to_csv(entry):
    file_exists = os.path.exists(CSV_LOG_PATH)
    with open(CSV_LOG_PATH, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(entry.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)


def main():
    print(f"\n📡 Fetching weather data for {CITY}...")
    weather_data = fetch_weather()
    entry = extract_station_entry(weather_data)
    log_to_csv(entry)
    print(f"✅ Logged entry for {entry['timestamp']} as station ID: {entry['station_id']}")


if __name__ == "__main__":
    main()