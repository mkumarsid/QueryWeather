import os
import duckdb

try:
    db_path = "weather_data.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Removed {db_path}")
    else:
        print(f"ℹ️ File not found: {db_path}")
except PermissionError as e:
    print(f"❌ Could not delete DB: {e}")
