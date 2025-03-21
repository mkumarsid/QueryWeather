import requests
import csv
from datetime import datetime

# Replace with your actual OpenWeatherMap API key
API_KEY = '5f416c6f2c4d94b658cb2be255c8c8c0'
CITY = 'Dublin'
UNITS = 'metric'

# API URL
url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&units={UNITS}&appid={API_KEY}"

# Make request
response = requests.get(url)
data = response.json()

# Extract required info
date = datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
temp = data['main']['temp']
humidity = data['main']['humidity']
wind_speed = data['wind']['speed']
weather = data['weather'][0]['description'].title()
city = data['name']
country = data['sys']['country']

# Print
print(f"{date} → {city}, {country}")
print(f"Weather: {weather}")
print(f"Temperature: {temp} °C")
print(f"Humidity: {humidity} %")
print(f"Wind Speed: {wind_speed} m/s")

# Save to CSV
with open("dublin_current_weather.csv", mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "City", "Country", "Weather", "Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)"])
    writer.writerow([date, city, country, weather, temp, humidity, wind_speed])

print("✅ Current weather data saved to 'dublin_current_weather.csv'")
