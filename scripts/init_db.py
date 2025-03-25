
from app.db.duck_db_utils import WeatherDB
from pathlib import Path

def build_weather_db():
    db = WeatherDB("weather_data.db")
    data_dir = Path(__file__).resolve().parent.parent / "tests/data"
    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in 'data/' folder.")
        return

    for csv in csv_files:
        print(f"Ingesting {csv.name}")
        db.insert_csv(str(csv))

    print("weather_data.db created with sample data.")

if __name__ == "__main__":
    build_weather_db()