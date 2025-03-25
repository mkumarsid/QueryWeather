from datetime import datetime, timedelta
import duckdb
import pandas as pd
from app.models import WeatherMetric
from utils.logger_service import get_logger
import os
from dotenv import load_dotenv

logger = get_logger(__name__)

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


class WeatherDB:
    def __init__(self, db_path="weather_data.db"):
        self.db_path = db_path
        self.con = duckdb.connect(self.db_path)

    def insert_csv(self, csv_path: str, table_name: str = "weather"):
        """
        Ingest sensor metrics CSV to database, The data is historical which is
        synthetic generated.
        """
        df = pd.read_csv(csv_path)
        logger.info(f"Processing CSV: {csv_path}")

        # Assume 'Datetime' is the expected column
        if "Datetime" not in df.columns:
            raise ValueError("❌ 'Datetime' column not found in the CSV.")

        df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")

        if df["Datetime"].isnull().all():
            raise ValueError("❌ 'Datetime' column could not be parsed.")

        # Normalize column names
        column_map = {
            "Temperature (°C)": "Temperature",
            "Humidity (%)": "Humidity",
            "Wind Speed (m/s)": "WindSpeed",
            "Weather Description": "WeatherDescription",
        }
        for csv_col, db_col in column_map.items():
            if csv_col in df.columns:
                df[db_col] = df[csv_col]

        required_columns = [
            "station_id",
            "city",
            "country",
            "Datetime",
            "Temperature",
            "Humidity",
            "WindSpeed",
            "WeatherDescription",
        ]
        df = df[required_columns]

        self._create_table_if_not_exists(table_name)

        self.con.register("df_temp", df)

        # Insert new rows only
        insert_query = f"""
            INSERT INTO {table_name}
            SELECT * FROM df_temp dt
            WHERE NOT EXISTS (
                SELECT 1 FROM {table_name} wt
                WHERE wt.station_id = dt.station_id AND wt.Datetime = dt.Datetime
            )
        """
        before_count = self.con.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]
        self.con.execute(insert_query)
        after_count = self.con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[
            0
        ]

        inserted = after_count - before_count
        logger.info(
            f"Inserted {inserted} new row(s) into '{table_name}' from {csv_path}"
        )

    def insert_metrics(self, metric: WeatherMetric, table_name: str = "weather"):
        """
        Insert weather metrics.
        """
        self._create_table_if_not_exists(table_name)
        df = pd.DataFrame([metric.dict()])
        self.con.register("df_post", df)
        self.con.execute(f"INSERT INTO {table_name} SELECT * FROM df_post")

    def _create_table_if_not_exists(self, table_name: str):
        """
        At startup create table "weather" in database if does'nt
        exists.
        """
        self.con.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                station_id VARCHAR,
                city VARCHAR,
                country VARCHAR,
                Datetime TIMESTAMP,
                Temperature DOUBLE,
                Humidity INTEGER,
                WindSpeed DOUBLE,
                WeatherDescription VARCHAR,
                UNIQUE(station_id, Datetime)
            );
        """
        )

    def get_sensor_details(self, station_ids=None, table_name="weather"):
        """
        Ingests live weather data (forecast + current) for multiple cities.
        Then returns the latest weather record for each station (by max Datetime).
        """
        from ingestion.ingest_openweather import WeatherIngestor

        cities = [
            {"city": "Dublin", "country": "Ireland"},
            {"city": "Galway", "country": "Ireland"},
        ]

        for location in cities:
            try:
                ingestor = WeatherIngestor(
                    api_key=API_KEY,
                    city=location["city"],
                    country=location["country"],
                )
                ingestor.ingest_forecast()
                ingestor.ingest_current_weather()
            except Exception as e:
                logger.info(f"Skipped ingestion for {location['city']}: {e}")

        # Latest row per station — NOT just MAX(Datetime) JOIN (which can be stale)
        subquery = f"""
            SELECT station_id, MAX(Datetime) AS latest_dt
            FROM {table_name}
            GROUP BY station_id
        """

        main_query = f"""
            SELECT w.*
            FROM {table_name} w
            INNER JOIN ({subquery}) latest
            ON w.station_id = latest.station_id AND w.Datetime = latest.latest_dt
        """

        if station_ids:
            ids = ",".join([f"'{sid}'" for sid in station_ids])
            main_query += f" WHERE w.station_id IN ({ids})"

        main_query += " ORDER BY w.station_id"

        return self.con.execute(main_query).fetchdf()

    def get_metric_stats(
        self,
        metric: str,
        stat: str,
        start_date=None,
        end_date=None,
        station_ids=None,
        city=None,
        table_name="weather",
    ):
        """
        Get metrics statistics for the given sensor/station id's based
        on city if provided.
        """
        valid_stats = ["avg", "min", "max", "sum"]
        if stat not in valid_stats:
            raise ValueError(f"Invalid stat '{stat}'")

        start_date, end_date = self._normalize_date_range(start_date, end_date)
        query = f"""
            SELECT station_id, city, country, {stat}({metric}) AS {stat}_{metric}
            FROM {table_name}
            WHERE Datetime BETWEEN '{start_date}' AND '{end_date}'
        """

        filters = []
        if station_ids:
            ids = ",".join([f"'{sid}'" for sid in station_ids])
            filters.append(f"station_id IN ({ids})")
        if city:
            filters.append(f"LOWER(city) = LOWER('{city}')")

        if filters:
            query += " AND " + " AND ".join(filters)

        query += " GROUP BY station_id, city, country"

        logger.info(f"Executing Query : {query}")
        return self.con.execute(query).fetchdf()

    def _normalize_date_range(self, start_date, end_date):
        """
        Normalise start and end dates according to the format of schema.
        """
        if not end_date:
            end_date = datetime.utcnow().date()
        if not start_date:
            start_date = end_date - timedelta(days=1)
        return start_date, end_date

    def close(self):
        self.con.close()
