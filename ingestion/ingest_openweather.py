import requests
import sys
import os
from app.db.duck_db_utils import WeatherDB, WeatherMetric
from datetime import datetime, timezone

# Add project root to path so that the app module is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class WeatherIngestor:
    def __init__(self, api_key: str, city: str, country: str, units: str = "metric"):
        # Basic input sanitization: strip whitespace from parameters
        self.api_key = api_key.strip()
        self.city = city.strip()
        self.country = country.strip()
        self.units = units.strip()
        self.db = WeatherDB()
        self.current_url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&units={self.units}&appid={self.api_key}"
        self.forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={self.city}&units={self.units}&appid={self.api_key}"


    def ingest_current_weather(self):
        print(f"🌐 Fetching Current URL: {self.current_url} for City {self.city}")
        response = requests.get(self.current_url)
        if response.status_code != 200:
            print(f"❌ Failed to fetch current weather data: {response.status_code} - {response.text}")
            return

        current = response.json()
    
        # ✅ Use API 'dt' field (UTC timestamp)
        dt = datetime.fromtimestamp(current["dt"], tz=timezone.utc)

        # Check if this current entry already exists
        exists = self.db.con.execute(
            f"SELECT COUNT(*) FROM weather WHERE Datetime = '{dt}'"
        ).fetchone()[0]
        if exists:
            print(f"⏭️ Skipping current weather — entry already exists for {dt}")
            return

        # Prepare data
        main = current["main"]
        wind = current.get("wind", {})
        weather_desc = current.get("weather", [{}])[0].get("description", "N/A")

        station_id = f"{self.city}_{int(current['dt'])}"  # Use city + timestamp instead of lat/lon

        metric = WeatherMetric(
            station_id=f"{self.city.upper()}_{current['coord']['lat']}_{current['coord']['lon']}",
            #station_id = f"{self.city}_{int(current['dt'])}",
            city=self.city,
            country=self.country,
            Datetime=dt,
            Temperature=main.get("temp"),
            Humidity=main.get("humidity"),
            WindSpeed=wind.get("speed"),
            WeatherDescription=weather_desc
        )

        self.db.insert_metrics(metric)
        print(f"✅ Ingested current weather at {dt} for {self.city}")

    from datetime import datetime, timezone

    def ingest_forecast(self):
        print(f"🌐 Fetching Forecast URL: {self.forecast_url} for City {self.city}")
        response = requests.get(self.forecast_url)

        if response.status_code != 200:
            raise Exception(f"❌ Failed to fetch forecast data: {response.status_code} - {response.text}")

        weather_data = response.json()
        entries = weather_data.get("list", [])
        if not entries:
            print("⚠️ No forecast data found in API response.")
            return

        for entry in entries:
            # ✅ Use timezone-aware datetime (UTC)
            dt = datetime.fromtimestamp(entry["dt"], tz=timezone.utc)

            # ⛔ Skip if entry already exists (exact datetime match)
            exists = self.db.con.execute(
                f"SELECT COUNT(*) FROM weather WHERE Datetime = '{dt}'"
            ).fetchone()[0]
            if exists:
                continue

            main = entry["main"]
            wind = entry.get("wind", {})
            weather_desc = entry.get("weather", [{}])[0].get("description", "N/A")

            metric = WeatherMetric(
                station_id=f"{self.city.upper()}_{weather_data['city']['coord']['lat']}_{weather_data['city']['coord']['lon']}",
                city=self.city,
                country=self.country,
                Datetime=dt,
                Temperature=main.get("temp"),
                Humidity=main.get("humidity"),
                WindSpeed=wind.get("speed"),
                WeatherDescription=weather_desc
            )
            self.db.insert_metrics(metric)
            print(f"✅ Ingested forecast entry at {dt.isoformat()} for {self.city}")

    
    def run(self):
        print("🚀 Starting ingestion pipeline for current weather data...")
        self.ingest_current_weather()
        print("🚀 Starting ingestion pipeline for forecast data...")
        self.ingest_forecast()
        self.db.close()

if __name__ == "__main__":
    # Use your public API key and desired parameters
    API_KEY = "5f416c6f2c4d94b658cb2be255c8c8c0"  # Replace with your actual key
    CITY = "Dublin"
    COUNTRY = "Ireland"
    
    ingestor = WeatherIngestor(api_key=API_KEY, city=CITY, country=COUNTRY, units="metric")
    ingestor.run()
