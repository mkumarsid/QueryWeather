import argparse
import random
from datetime import datetime, timedelta

import pandas as pd


def generate_synthetic_weather_data(start_date: str, end_date: str, output_file: str):
    date_range = pd.date_range(start=start_date, end=end_date, freq="H")

    stations = [
        {"station_id": "DUBLIN_53.33_-6.25", "city": "Dublin", "country": "Ireland"},
        {"station_id": "GALWAY_53.27_-9.05", "city": "Galway", "country": "Ireland"},
    ]

    weather_descriptions = [
        "clear sky",
        "light rain",
        "overcast",
        "fog",
        "sunny",
        "cloudy",
    ]

    records = []
    for dt in date_range:
        for station in stations:
            record = {
                "station_id": station["station_id"],
                "city": station["city"],
                "country": station["country"],
                "Datetime": dt,
                "Temperature": round(random.uniform(5.0, 25.0), 2),
                "Humidity": random.randint(50, 100),
                "WindSpeed": round(random.uniform(0.5, 15.0), 2),
                "WeatherDescription": random.choice(weather_descriptions),
            }
            records.append(record)

    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    print(
        f"✅ Generated {len(df)} rows of synthetic weather data for {len(stations)} stations."
    )
    print(f"📄 Saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic weather data for Dublin and Galway."
    )
    parser.add_argument(
        "--start", type=str, required=True, help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--end", type=str, required=True, help="End date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--out", type=str, default="synthetic_weather.csv", help="Output CSV file name"
    )

    args = parser.parse_args()

    generate_synthetic_weather_data(args.start, args.end, args.out)
