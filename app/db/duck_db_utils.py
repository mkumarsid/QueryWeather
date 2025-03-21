import duckdb
import pandas as pd
from datetime import datetime, timedelta
#from app.db.models import WeatherMetric

from app.db.model import WeatherMetric


class WeatherDB:
    def __init__(self, db_path='weather_data.db'):
        self.db_path = db_path
        self.con = duckdb.connect(self.db_path)

    # def insert_csv(self, csv_path: str, table_name: str = 'weather'):
    #     df = pd.read_csv(csv_path, parse_dates=['Datetime'])
    #     self._create_table_if_not_exists(table_name)
    #     self.con.register("df_temp", df)
    #     self.con.execute(f"INSERT INTO {table_name} SELECT * FROM df_temp")
    
    def insert_csv(self, csv_path: str, table_name: str = 'weather'):
        df = pd.read_csv(csv_path)

        print("🧪 Raw CSV columns:", df.columns)

    # Handle datetime
        datetime_col = None
        for col in df.columns:
            if col.lower().strip() in ['datetime', 'date time', 'timestamp']:
                datetime_col = col
                break

        if not datetime_col:
            raise ValueError("❌ No datetime column found!")

        df['Datetime'] = pd.to_datetime(df[datetime_col], errors='coerce')

        print("📅 Parsed Datetime preview:")
        print(df[['Datetime']].head())

        if df['Datetime'].isnull().all():
            raise ValueError("❌ All Datetime values failed to parse.")

        # Optional: normalize column names
        column_map = {
            'Temperature (°C)': 'Temperature',
            'Humidity (%)': 'Humidity',
            'Wind Speed (m/s)': 'WindSpeed',
            'Weather Description': 'WeatherDescription'
        }
        for csv_col, db_col in column_map.items():
            if csv_col in df.columns:
                df[db_col] = df[csv_col]

        print("📊 Final DataFrame columns before insert:", df.columns)

        required_columns = ['station_id', 'city', 'country', 'Datetime', 'Temperature', 'Humidity', 'WindSpeed', 'WeatherDescription']
        df = df[required_columns]

        self._create_table_if_not_exists(table_name)
        self.con.register("df_temp", df)
        self.con.execute(f"INSERT INTO {table_name} SELECT * FROM df_temp")
        print(f"✅ Inserted {len(df)} rows into '{table_name}'")



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
                WeatherDescription VARCHAR
            );
        """)

    # def get_sensor_details(self, station_ids=None, table_name='weather'):
    #     query = f"SELECT DISTINCT station_id, city, country FROM {table_name}"
    #     if station_ids:
    #         ids = ','.join([f"'{sid}'" for sid in station_ids])
    #         query += f" WHERE station_id IN ({ids})"
    #     return self.con.execute(query).fetchdf()
    
    def get_sensor_details(self, station_ids=None, table_name='weather'):
        """
        Returns sensor details along with the latest reading for Temperature, Humidity, and WindSpeed.
        """
        query = f"""
            SELECT t1.station_id, t1.city, t1.country, t1.Temperature, t1.Humidity, t1.WindSpeed
            FROM {table_name} t1
            JOIN (
                SELECT station_id, MAX(Datetime) as max_dt
                FROM {table_name}
                GROUP BY station_id
            ) t2 ON t1.station_id = t2.station_id AND t1.Datetime = t2.max_dt
        """
        if station_ids:
            ids = ','.join([f"'{sid}'" for sid in station_ids])
            query += f" WHERE t1.station_id IN ({ids})"
        return self.con.execute(query).fetchdf()

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

    def close(self):
        self.con.close()