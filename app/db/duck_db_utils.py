import duckdb
import pandas as pd
from datetime import datetime, timedelta
from app.db.model import WeatherMetric


class WeatherDB:
    def __init__(self, db_path='weather_data.db'):
        self.db_path = db_path
        self.con = duckdb.connect(self.db_path)
        
    def insert_csv(self, csv_path: str, table_name: str = 'weather'):

        df = pd.read_csv(csv_path)
        print(f"📥 Processing CSV: {csv_path}")
        print("🧪 Raw CSV columns:", df.columns)
        
        # Assume 'Datetime' is the expected column
        if 'Datetime' not in df.columns:
            raise ValueError("❌ 'Datetime' column not found in the CSV.")

        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')

        if df['Datetime'].isnull().all():
            raise ValueError("❌ 'Datetime' column could not be parsed.")

        # Normalize column names
        column_map = {
            'Temperature (°C)': 'Temperature',
            'Humidity (%)': 'Humidity',
            'Wind Speed (m/s)': 'WindSpeed',
            'Weather Description': 'WeatherDescription'
        }
        for csv_col, db_col in column_map.items():
            if csv_col in df.columns:
                df[db_col] = df[csv_col]

        required_columns = [
            'station_id', 'city', 'country',
            'Datetime', 'Temperature', 'Humidity', 'WindSpeed', 'WeatherDescription'
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
        before_count = self.con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        self.con.execute(insert_query)
        after_count = self.con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

        inserted = after_count - before_count
        print(f"✅ Inserted {inserted} new row(s) into '{table_name}' from {csv_path}")

    
    # def insert_csv(self, csv_path: str, table_name: str = 'weather'):
    #     df = pd.read_csv(csv_path)

    #     print("🧪 Raw CSV columns:", df.columns)

    # # Handle datetime
    #     datetime_col = None
    #     for col in df.columns:
    #         if col.lower().strip() in ['datetime', 'date time', 'timestamp']:
    #             datetime_col = col
    #             break

    #     if not datetime_col:
    #         raise ValueError("❌ No datetime column found!")

    #     df['Datetime'] = pd.to_datetime(df[datetime_col], errors='coerce')

    #     print("📅 Parsed Datetime preview:")
    #     print(df[['Datetime']].head())

    #     if df['Datetime'].isnull().all():
    #         raise ValueError("❌ All Datetime values failed to parse.")

    #     # Optional: normalize column names
    #     column_map = {
    #         'Temperature (°C)': 'Temperature',
    #         'Humidity (%)': 'Humidity',
    #         'Wind Speed (m/s)': 'WindSpeed',
    #         'Weather Description': 'WeatherDescription'
    #     }
    #     for csv_col, db_col in column_map.items():
    #         if csv_col in df.columns:
    #             df[db_col] = df[csv_col]

    #     print("📊 Final DataFrame columns before insert:", df.columns)

    #     required_columns = ['station_id', 'city', 'country', 'Datetime', 'Temperature', 'Humidity', 'WindSpeed', 'WeatherDescription']
    #     df = df[required_columns]

    #     self._create_table_if_not_exists(table_name)
    #     self.con.register("df_temp", df)
    #     self.con.execute(f"INSERT INTO {table_name} SELECT * FROM df_temp")
    #     print(f"✅ Inserted {len(df)} rows into '{table_name}'")


    def insert_metrics(self, metric: WeatherMetric, table_name: str = 'weather'):
        self._create_table_if_not_exists(table_name)
        df = pd.DataFrame([metric.dict()])
        self.con.register("df_post", df)
        self.con.execute(f"INSERT INTO {table_name} SELECT * FROM df_post")

    
    def _create_table_if_not_exists(self, table_name: str):
        self.con.execute(f"""
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
        """)
        
    def get_sensor_details(self, station_ids=None, table_name='weather'):
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
                    api_key="5f416c6f2c4d94b658cb2be255c8c8c0",
                    city=location["city"],
                    country=location["country"]
                )
                ingestor.ingest_forecast()
                ingestor.ingest_current_weather()
            except Exception as e:
                print(f"⚠️ Skipped ingestion for {location['city']}: {e}")

        # ✅ Latest row per station — NOT just MAX(Datetime) JOIN (which can be stale)
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
            ids = ','.join([f"'{sid}'" for sid in station_ids])
            main_query += f" WHERE w.station_id IN ({ids})"

        main_query += " ORDER BY w.station_id"

        return self.con.execute(main_query).fetchdf()


    # def get_sensor_details(self, station_ids=None, table_name='weather'):
    #     """
    #     Triggers live forecast ingestion and returns the latest sensor readings 
    #     for each station including Temperature, Humidity, WindSpeed and Datetime.
    #     Falls back to existing DuckDB data if API call fails.
    #     """
    #     from ingestion.ingest_openweather import WeatherIngestor
        
    #     cities = [
    #     {"city": "Dublin", "country": "Ireland"},
    #     {"city": "Galway", "country": "Ireland"},
    #     ]

    #     # Step 1: Ingest live data for all cities
    #     for location in cities:
    #         try:
    #             ingestor = WeatherIngestor(
    #                 api_key="5f416c6f2c4d94b658cb2be255c8c8c0",
    #                 city=location["city"],
    #                 country=location["country"]
    #             )
    #             ingestor.ingest_forecast()
    #             ingestor.ingest_current_weather()
    #         except Exception as e:
    #             print(f"⚠️ Ingestion failed for {location['city']}: {e} — using existing data.")


    #     # Step 2: Return latest readings per station using cleaner query
    #     filter_clause = ""
    #     if station_ids:
    #         ids = ','.join([f"'{sid}'" for sid in station_ids])
    #         filter_clause = f"AND station_id IN ({ids})"

    #     query = f"""
    #         SELECT *
    #         FROM {table_name}
    #         WHERE (station_id, Datetime) IN (
    #             SELECT station_id, MAX(Datetime)
    #             FROM {table_name}
    #             GROUP BY station_id
    #         )
    #         {filter_clause}
    #         ORDER BY station_id
    #     """

    #     return self.con.execute(query).fetchdf()

 

    # def get_sensor_details(self, station_ids=None, table_name='weather'):
    #     """
    #     Triggers live forecast ingestion and returns the latest sensor readings 
    #     for each station including Temperature, Humidity, and WindSpeed.
    #     Falls back to existing DuckDB data if API call fails.
    #     """
    #     from ingestion.ingest_openweather import WeatherIngestor
    #     # Step 1: Try ingesting live forecast data
    #     try:
    #         API_KEY = "5f416c6f2c4d94b658cb2be255c8c8c0"
    #         CITY = "Dublin"
    #         COUNTRY = "Ireland"
    #         ingestor = WeatherIngestor(api_key=API_KEY, city=CITY, country=COUNTRY)
    #         ingestor.ingest_forecast()
    #         ingestor.ingest_current_weather()
    #     except Exception as e:
    #         print(f"⚠️ Ingestion failed or skipped: {e} — using existing DuckDB data.")

    #     # Step 2: Return latest readings per station
    #     query = f"""
    #         SELECT 
    #             t1.station_id, 
    #             t1.city, 
    #             t1.country, 
    #             t1.Temperature, 
    #             t1.Humidity, 
    #             t1.WindSpeed,
    #             CAST(t1.Datetime AS DATE) AS DataDate,
    #             t1.Datetime
    #             FROM {table_name} t1
    #             JOIN (
    #                 SELECT station_id, MAX(Datetime) AS max_dt
    #                 FROM {table_name}
    #                 GROUP BY station_id
    #             ) t2 ON t1.station_id = t2.station_id AND t1.Datetime = t2.max_dt
    #         """
    #     if station_ids:
    #         ids = ','.join([f"'{sid}'" for sid in station_ids])
    #         query += f" WHERE t1.station_id IN ({ids})"

    #     return self.con.execute(query).fetchdf()



    # def get_sensor_details(self, station_ids=None, table_name='weather'):
    #     """
    #     Returns sensor details along with the latest reading for Temperature, Humidity, and WindSpeed.
    #     """
    #     query = f"""
    #         SELECT t1.station_id, t1.city, t1.country, t1.Temperature, t1.Humidity, t1.WindSpeed
    #         FROM {table_name} t1
    #         JOIN (
    #             SELECT station_id, MAX(Datetime) as max_dt
    #             FROM {table_name}
    #             GROUP BY station_id
    #         ) t2 ON t1.station_id = t2.station_id AND t1.Datetime = t2.max_dt
    #     """
    #     if station_ids:
    #         ids = ','.join([f"'{sid}'" for sid in station_ids])
    #         query += f" WHERE t1.station_id IN ({ids})"
    #     return self.con.execute(query).fetchdf()
    

    def get_metrics_average(self, metrics, start_date=None, end_date=None, table_name='weather'):
        start_date, end_date = self._normalize_date_range(start_date, end_date)
        select_clause = ', '.join([f"avg({m}) AS avg_{m}" for m in metrics])
        query = f"""
            SELECT station_id, city, country, {select_clause}
            FROM {table_name}
            WHERE Datetime BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY station_id, city, country
        """
        return self.con.execute(query).fetchdf()

    def get_metric_stats(self, metric: str, stat: str, start_date=None, end_date=None, table_name='weather'):
        valid_stats = ['avg', 'min', 'max', 'sum']
        if stat not in valid_stats:
            raise ValueError(f"Invalid stat '{stat}'")
        start_date, end_date = self._normalize_date_range(start_date, end_date)
        query = f"""
            SELECT station_id, city, country, {stat}({metric}) AS {stat}_{metric}
            FROM {table_name}
            WHERE Datetime BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY station_id, city, country
        """
        return self.con.execute(query).fetchdf()

    def _normalize_date_range(self, start_date, end_date):
        if not end_date:
            end_date = datetime.utcnow().date()
        if not start_date:
            start_date = end_date - timedelta(days=1)
        return start_date, end_date

    def get_raw_metrics(self, metrics, start_date=None, end_date=None, table_name='weather'):
        start_date, end_date = self._normalize_date_range(start_date, end_date)
        cols = ', '.join(['station_id', 'city', 'country', 'Datetime'] + metrics)
        query = f"""
            SELECT {cols}
            FROM {table_name}
            WHERE Datetime BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY Datetime
        """
        return self.con.execute(query).fetchdf()

    def close(self):
        self.con.close()