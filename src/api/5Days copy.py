import requests
import time
import csv
from datetime import datetime, timedelta

API_KEY = '5f416c6f2c4d94b658cb2be255c8c8c0'
LAT = 53.3498
LON = -6.2603

# Get timestamps for previous 5 days
timestamps = [(datetime.utcnow() - timedelta(days=i)).replace(hour=12, minute=0, second=0, microsecond=0) for i in range(1, 6)]

# CSV setup
csv_filename = "dublin_last_5_days_weather.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)", "Weather Description"])

    for ts in timestamps:
        unix_ts = int(ts.timestamp())
        url = (
            f"https://api.openweathermap.org/data/2.5/onecall/timemachine"
            f"?lat={LAT}&lon={LON}&dt={unix_ts}&units=metric&appid={API_KEY}"
        )

        response = requests.get(url)
        data = response.json()

        if 'current' in data:
            temp = data['current']['temp']
            humidity = data['current']['humidity']
            wind = data['current']['wind_speed']
            description = data['current']['weather'][0]['description'].title()
            date_str = ts.strftime('%Y-%m-%d')

            writer.writerow([date_str, temp, humidity, wind, description])
            print(f"✅ Collected data for {date_str}")
        else:
            print(f"⚠️ Skipped {ts.strftime('%Y-%m-%d')} – no data returned")

print(f"\n✅ Weather data for the past 5 days saved to '{csv_filename}'")
