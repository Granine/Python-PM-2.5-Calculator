
'''
------------------Start of reading------------------------
Date: April 26, 2022
Author: Guan Huang
Project Description: Air pollutant PM2.5 calculator within input region (average, and more)
Project Purpose: Create a tool that can be easily embedded into any software application
Additional Requirements: 
- Parameter passible through python arguments
- Parameter passible through function arguments
- Concurrency safe
'''

'''
sample powershell command:
sample 8 times per minute for 2 minute (3 station)
    python pm25.py 39 116 41 116.04 2 8
sample 1 times per minute for 3 minute
    python pm25.py 39 116 41 116.04 3
sample 1 times per minute for 5 minute
    python pm25.py 39 116 41 116.04 

'''

import sys
import json
import requests
import time

'''calculate average of air pollutant PM2.5 over n minutes for each station and average of all station in a specified region
def pm25Calc(lat1, lng1, lat2, lng2, sampling_time=5, sampling_Rate=1):
@param: lat1:float: latitude of first position to lock
@param: lng1:float: longitude of first position to lock
@param: lat2:float: latitude of second position to lock
@param: lng2:float: longitude of second position to lock
@param: sampling_time:float: time to sample (second), suggested time: 0~10
@param: sampling_Rate:int: number of times to sample per second (times/second), suggested rate: 0.1~16
@return: None
arguments 1: lat1
arguments 2: lng1
arguments 3: lat2
arguments 4: lng2
arguments 5: sampling_time
arguments 6: sampling_Rate
'''
def pm25Calc(lat1, lng1, lat2, lng2, sampling_time=5, sampling_Rate=1):
    # Parameter and Argument normalization
    lat1 = sys.argv[1] if len(sys.argv) >=5 else lat1
    lng1 = sys.argv[2] if len(sys.argv) >=5 else lng1
    lat2 = sys.argv[3] if len(sys.argv) >=5 else lat2
    lng2 = sys.argv[4] if len(sys.argv) >=5 else lng2
    sampling_time = sys.argv[5] if len(sys.argv) >=6 else sampling_time
    sampling_rate = sys.argv[6] if len(sys.argv) >=7 else sampling_rate
    if len(sys.argv) >= 8:
        raise Warning("Input argument number beyond needed, extra argument ignored.")

    #get stations based on location region specified
    stations = getStations(lat1, lng1, lat2, lng2)
    stationName = getStationsName(lat1, lng1, lat2, lng2) # this is added for readability of result
    
    #station ID is a better indication of station globally
    pm25_per_station = []

    #calculate total number of times sampling, round this to get integer
    totalSampleNumber = round(sampling_time * sampling_Rate) if totalSampleNumber >= 1 else 1

    #first sample and create array to record sample for each station
    for station in stations:
        pm25_per_station.append(getPM25(station)/totalSampleNumber)

    #sampling afterword
    for _ in range(totalSampleNumber - 1):
        #see above "known issues" for reasons to use sleep
        time.sleep(60/sampling_Rate)
        for station in range(len(stations)):
            pm25_per_station[station]+=getPM25(station)/totalSampleNumber

    #printing
    pm25avg = sum(pm25_per_station)/len(pm25_per_station)
    #place data in map for return 
    stationData = dict(zip(stationName, pm25_per_station))
    print("PM 2.5 for each station:")
    for stationCount in range(len(stationName)):
        print(list(stationData.items())[stationCount])

    #if consistent format as API is needed
    #print(stationData)
    print("Average PM 2.5 for all stations in region: ", pm25avg)
    return stationData

'''search for all monitor station in defined region
@param: lat1:float: latitude of first position to lock
@param: lng1:float: longitude of first position to lock
@param: lat2:float: latitude of second position to lock
@param: lng2:float: longitude of second position to lock
@return: Array of station ID in region (using ID instead of name as searcg by stations do not return city name needed for city feed
'''
def getStations(lat1, lng1, lat2, lng2):
    response = requests.get(("https://api.waqi.info//map/bounds?token=a680e3cd0496283661a9ab60a52c5a81e0e9c807&latlng="+ lat1 +","+ lng1 +","+ lat2 + "," + lng2))
    stationInArea = json.loads(response.text)
    stations = []
    for x in stationInArea["data"]:
        stations.append(x["uid"])
    return stations

'''search for all monitor station in defined region
@param: lat1:float: latitude of first position to lock
@param: lng1:float: longitude of first position to lock
@param: lat2:float: latitude of second position to lock
@param: lng2:float: longitude of second position to lock
@return: list: station name for printing
'''

def getStationsName(lat1, lng1, lat2, lng2):
    response = requests.get(("https://api.waqi.info//map/bounds?token=a680e3cd0496283661a9ab60a52c5a81e0e9c807&latlng="+ lat1 +","+ lng1 +","+ lat2 + "," + lng2))
    stationInArea = json.loads(response.text)
    stations = []
    for x in stationInArea["data"]:
        stations.append(x["station"]["name"])
    return stations

'''
@param stationID: id of the station to query
@return: current pm2.5 data of station
'''
def getPM25(stationID):
    response = requests.get("https://api.waqi.info/feed/@"+str(stationID)+"/?token=a680e3cd0496283661a9ab60a52c5a81e0e9c807")
    stationData = json.loads(response.text)
    return stationData["data"]["iaqi"]["pm25"]["v"]


if __name__ == "__main__":
    print (int(1.1))
    print (round(1111.9))
    #pm25Calc()