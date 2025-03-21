#needed to make web requests
import requests

#store the data we get as a dataframe
# import pandas as pd

#convert the response as a strcuctured json
import json

#mathematical operations on lists
import numpy as np

#parse the datetimes we get from NOAA
from datetime import datetime

#add the access token you got from NOAA
token = 'RheTAHPnhuHOxcTxIoRBGvATJjfRxLKX'

# Station
station_id = 'GHCND:US1CAMR0037'

#initialize lists to store data
dates_temp = []
dates_prcp = []
temps = []
minT = []
maxT = []
prcp = []

#for each year from 2019-2020 ...
for year in range(2019, 2020):
    year = str(year)
    print('working on year '+year)
    
    #make the api call
    r = requests.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&datatypeid=TAVG&datatypeid=TMAX&limit=1000&stationid='+station_id+'&startdate='+year+'-01-01&enddate='+year+'-12-31', headers={'token':token})
    r2 = requests.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&datatypeid=TMIN&datatypeid=PRCP&limit=1000&stationid='+station_id+'&startdate='+year+'-01-01&enddate='+year+'-12-31', headers={'token':token})

    #load the api response as a json
    d = json.loads(r.text)
    d2 = json.loads(r2.text)
    
    # print(d)
    # print(d2)

    #get all items in the response which are average temperature readings
    avg_temps = [item for item in d['results'] if item['datatype']=='TAVG']
    min_temps = [item for item in d2['results'] if item['datatype']=='TMIN']
    max_temps = [item for item in d['results'] if item['datatype']=='TMAX']
    precp = [item for item in d2['results'] if item['datatype']=='PRCP']

    print(avg_temps, min_temps, max_temps, precp)
    dates_temp += [item['date'] for item in avg_temps]
    #get the actual average temperature from all average temperature readings
    temps += [item['value'] for item in avg_temps]
    minT += [item['value'] for item in min_temps]
    maxT += [item['value'] for item in max_temps]
    prcp += [item['value'] for item in precp]