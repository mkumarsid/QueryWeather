from app.db.duck_db_utils import WeatherDB

db = WeatherDB()


def shutdown_db():
    db.close()
