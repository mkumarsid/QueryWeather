import pytest
from app.db.duck_db_utils import WeatherDB
from datetime import date

@pytest.fixture(scope="function")
def db():
    db = WeatherDB(":memory:")
    db.con.execute("""
        CREATE TABLE weather (
            station_id VARCHAR, city VARCHAR, country VARCHAR,
            Datetime TIMESTAMP, Temperature DOUBLE, Humidity INTEGER,
            WindSpeed DOUBLE, WeatherDescription VARCHAR
        )
    """)
    return db

def test_metric_stats_with_dummy_data(db):
    db.con.execute("""
        INSERT INTO weather VALUES 
        ('DUB1', 'Dublin', 'Ireland', '2025-03-01 12:00:00', 12.5, 60, 5.2, 'clear')
    """)

    df = db.get_metric_stats(
        "Temperature", "avg",
        start_date=date(2025, 3, 1),
        end_date=date(2025, 3, 2)
    )

    assert not df.empty
    assert "avg_Temperature" in df.columns

def test_invalid_stat_raises_value_error(db):
    with pytest.raises(ValueError):
        db.get_metric_stats("Temperature", "median")

def test_out_of_range_date_returns_empty(db):
    db.con.execute("""
        INSERT INTO weather VALUES 
        ('DUB1', 'Dublin', 'Ireland', '2025-03-01 12:00:00', 12.5, 60, 5.2, 'clear')
    """)
    df = db.get_metric_stats("Temperature", "avg", start_date=date(2030, 1, 1), end_date=date(2030, 1, 2))
    assert df.empty

def test_unknown_station_id_filter(db):
    db.con.execute("""
        INSERT INTO weather VALUES 
        ('DUB1', 'Dublin', 'Ireland', '2025-03-01 12:00:00', 12.5, 60, 5.2, 'clear')
    """)
    df = db.get_metric_stats("Temperature", "avg", station_ids=["FAKE1"])
    assert df.empty