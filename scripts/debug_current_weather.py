from datetime import datetime, timezone

import requests

# API details
API_KEY = "5f416c6f2c4d94b658cb2be255c8c8c0"
CITY = "Dublin"
UNITS = "metric"

url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&units={UNITS}&appid={API_KEY}"

# Request current weather
response = requests.get(url)
if response.status_code != 200:
    raise Exception(
        f"❌ Failed to fetch current weather: {response.status_code} - {response.text}"
    )

data = response.json()

# Extract datetime and convert to UTC
dt = datetime.fromtimestamp(data["dt"], tz=timezone.utc)
dt_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")

# Extract key weather data
temp = data["main"].get("temp")
humidity = data["main"].get("humidity")
wind_speed = data["wind"].get("speed")
weather = data.get("weather", [{}])[0].get("description", "N/A")

print(f"\n🌤️ Current Weather in {CITY} ({dt_str})")
print("-" * 50)
print(f"🌡️ Temperature: {temp} °C")
print(f"💧 Humidity: {humidity}%")
print(f"🌬️ Wind Speed: {wind_speed} m/s")
print(f"🌥️ Weather: {weather}")
print("-" * 50)
