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
        self._create_table_if_not_exists(table_name)
        count = self.con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        if count > 0:
            print("ℹ️ Data already exists, skipping CSV insert.")
            return
        df = pd.read_csv(csv_path, parse_dates=['Datetime'])
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

    def get_sensor_details(self, station_ids=None, table_name='weather'):
        query = f"SELECT DISTINCT station_id, city, country FROM {table_name}"
        if station_ids:
            ids = ','.join([f"'{sid}'" for sid in station_ids])
            query += f" WHERE station_id IN ({ids})"
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