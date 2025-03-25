# tests/test_duckdb_utils.py

import pytest
from app.db.duck_db_utils import WeatherDB
from datetime import date

@pytest.fixture(scope="module")
def db():
    return WeatherDB(":memory:")

def test_metric_stats_with_dummy_data(db):
    db.con.execute("""
        CREATE TABLE weather (
            station_id VARCHAR, city VARCHAR, country VARCHAR,
            Datetime TIMESTAMP, Temperature DOUBLE, Humidity INTEGER,
            WindSpeed DOUBLE, WeatherDescription VARCHAR
        )
    """)
    db.con.execute("""
        INSERT INTO weather VALUES 
        ('DUB1', 'Dublin', 'Ireland', '2025-03-01 12:00:00', 12.5, 60, 5.2, 'clear')
    """)

    start = date(2025, 3, 1)
    end = date(2025, 3, 2)

    df = db.get_metric_stats("Temperature", "avg", start_date=start, end_date=end)

    print("Start:", start, "| End:", end)
    print("Returned DataFrame:\n", df)
    assert not df.empty
    assert "avg_Temperature" in df.columns

def test_invalid_stat_raises_value_error(db):
    """Should raise ValueError for unsupported stat."""
    with pytest.raises(ValueError) as exc_info:
        db.get_metric_stats("Temperature", "median")
    assert "Invalid stat" in str(exc_info.value)

def test_out_of_range_date_returns_empty(db):
    """Should return empty result for out-of-range dates."""
    db.con.execute("""
        INSERT INTO weather VALUES 
        ('DUB1', 'Dublin', 'Ireland', '2025-03-01 12:00:00', 12.5, 60, 5.2, 'clear')
    """)
    df = db.get_metric_stats("Temperature", "avg", start_date=date(2030, 1, 1), end_date=date(2030, 1, 2))
    assert df.empty

def test_unknown_station_id_filter(db):
    """Should return empty when station_id doesn't match."""
    df = db.get_metric_stats("Temperature", "avg", station_ids=["FAKE1"])
    assert df.empty
