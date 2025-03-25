from datetime import datetime

import requests


def fetch_weather(city: str):
    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Failed to fetch weather: {e}")
        return

    # --- Current weather ---
    current = data["current_condition"][0]
    print(f"\n🌍 Weather for {city.title()} — Current Conditions")
    print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌡️  Temperature: {current['temp_C']} °C")
    print(f"💧 Humidity: {current['humidity']}%")
    print(f"🌬️  Wind Speed: {current['windspeedKmph']} km/h")
    print(f"🌤️  Condition: {current['weatherDesc'][0]['value']}")

    # --- Hourly forecast for today ---
    today = data["weather"][0]
    print(f"\n📅 Hourly Forecast for {today['date']} in {city.title()}")
    for hour in today["hourly"]:
        time_hr = int(hour["time"]) // 100
        time_label = f"{time_hr:02d}:00"
        print(f"\n🕒 {time_label}")
        print(f"  🌡️ Temp: {hour['tempC']} °C")
        print(f"  💧 Humidity: {hour['humidity']}%")
        print(f"  🌬️ Wind: {hour['windspeedKmph']} km/h")
        print(f"  🌤️ Desc: {hour['weatherDesc'][0]['value']}")


if __name__ == "__main__":
    fetch_weather("Dublin")
