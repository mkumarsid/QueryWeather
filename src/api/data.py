import duckdb
from datetime import datetime, timedelta

# Connect to DuckDB (or create a new one)
con = duckdb.connect("weather_data.db")

# Create a table for sensor data
con.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        sensor_id VARCHAR,
        timestamp TIMESTAMP,
        temperature DOUBLE,
        humidity DOUBLE,
        wind_speed DOUBLE
    )
""")

# Insert sample data
sample_data = [
    ("sensor_1", datetime.utcnow() - timedelta(days=i), 20.5 + i, 50 + i, 10 + i)
    for i in range(7)
]
con.executemany("""
    INSERT INTO sensor_data (sensor_id, timestamp, temperature, humidity, wind_speed)
    VALUES (?, ?, ?, ?, ?)
""", sample_data)

# Query average temperature and humidity for the last week
query = """
    SELECT sensor_id,
           AVG(temperature) AS avg_temperature,
           AVG(humidity) AS avg_humidity
    FROM sensor_data
    WHERE timestamp >= NOW() - INTERVAL '7 days'
    GROUP BY sensor_id
"""

result = con.execute(query).fetchall()

# Print query result
for row in result:
    print(row)

# Close connection
con.close()
