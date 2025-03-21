import requests
import csv
from datetime import datetime

API_KEY = '5f416c6f2c4d94b658cb2be255c8c8c0'  # Replace with your actual key
CITY = 'Dublin'
UNITS = 'metric'

# API URL
url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&units={UNITS}&appid={API_KEY}"

# Request data
response = requests.get(url)
data = response.json()

# Prepare CSV
csv_file = "dublin_5_day_forecast.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Datetime", "Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)", "Weather Description"])

    for entry in data['list']:
        timestamp = datetime.utcfromtimestamp(entry['dt']).strftime('%Y-%m-%d %H:%M:%S')
        temp = entry['main']['temp']
        humidity = entry['main']['humidity']
        wind = entry['wind']['speed']
        description = entry['weather'][0]['description'].title()

        writer.writerow([timestamp, temp, humidity, wind, description])

print(f"✅ 5-day forecast saved to {csv_file}")
