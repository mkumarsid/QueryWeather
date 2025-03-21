import duckdb
import pandas as pd


def insert_weather_csv_to_duckdb(csv_path: str, db_path: str = "weather_data.db", table_name: str = "weather"):
    """
    Insert weather data from a CSV file into a DuckDB database table.

    Parameters:
    - csv_path: Path to the CSV file
    - db_path: Path to the DuckDB database (default: 'weather_data.db')
    - table_name: Name of the table to create or insert into (default: 'weather')
    """
    try:
        # Load CSV into DataFrame
        df = pd.read_csv(csv_path, parse_dates=['Datetime'])

        # Connect to DuckDB (creates if doesn't exist)
        con = duckdb.connect(database=db_path)

        # Create table if it doesn't exist
        con.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                Datetime TIMESTAMP,
                Temperature DOUBLE,
                Humidity INTEGER,
                WindSpeed DOUBLE,
                WeatherDescription VARCHAR
            );
        """)

        # Insert data
        con.register("temp_df", df)
        con.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")

        print(f"✅ Inserted {len(df)} rows into '{table_name}' table in '{db_path}'.")

    except Exception as e:
        print(f"❌ Error: {e}")


def query_weather_data(db_path: str = "weather_data.db", table_name: str = "weather", 
                        start_date: str = None, end_date: str = None):
    """
    Query weather data from DuckDB with optional date range filter.

    Parameters:
    - db_path: Path to the DuckDB database (default: 'weather_data.db')
    - table_name: Name of the table to query (default: 'weather')
    - start_date: Optional start date in 'YYYY-MM-DD' format
    - end_date: Optional end date in 'YYYY-MM-DD' format

    Returns:
    - Pandas DataFrame containing the result
    """
    try:
        con = duckdb.connect(database=db_path)
        query = f"SELECT * FROM {table_name}"

        if start_date and end_date:
            query += f" WHERE Datetime BETWEEN '{start_date}' AND '{end_date}'"

        df = con.execute(query).fetchdf()
        return df

    except Exception as e:
        print(f"❌ Query error: {e}")
        return pd.DataFrame()


# Example usage:
if __name__ == "__main__":
    insert_weather_csv_to_duckdb("dublin_last_5_days_hourly.csv")

    # Example query usage:
    result = query_weather_data(start_date="2025-03-17", end_date="2025-03-19")
    print(result)