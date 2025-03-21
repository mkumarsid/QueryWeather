import pandas as pd

df = pd.read_csv(r"C:\Users\madkumar\Python-Learning\QueryWeather\data\dublin_last_5_days_hourly_with_station_new.csv", parse_dates=['Date Time'])
df['Datetime'] = df['Date Time']  # map it to expected schema
