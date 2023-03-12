
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

sample powershell command:
sample 8 times per minute for 2 minutes (3 stations)
    python pm25.py 39 116 41 116.04 2 8
sample 1 times per minute for 3 minutes
    python pm25.py 39 116 41 116.04 3
sample 1 times per minute for 5 minutes
    python pm25.py 39 116 41 116.04 
'''

import sys
import json
import requests
import time
import os

class PM25_Calculator:
    '''A PM 2.5 calculator for a specified square area'''
    
    waqi_token:str = "" # one can but should not be leaving tokens here, environment variable is suggested
    
    '''calculate average of air pollutant PM2.5 over n minutes for each station and average of all station in a specified region
    def pm25Calc(lat1, lng1, lat2, lng2, sampling_count=5, sampling_time=1):
    @param: lat1:float: latitude of first position to lock
    @param: lng1:float: longitude of first position to lock
    @param: lat2:float: latitude of second position to lock
    @param: lng2:float: longitude of second position to lock
    @param: waqi_token:string: time the sampling will last in minute, suggested time: <10 min
    '''
    def __init__(self, lat1, lng1, lat2, lng2, waqi_token=""):
        # Parameter and Argument normalization
        self.lat1:float = lat1
        self.lng1:float = lng1
        self.lat2:float = lat2
        self.lng2:float = lng2
        
        # if waqi passed in, it should have the highest priority
        if waqi_token:
            self.waqi_token = waqi_token
        # then read from environment variable
        elif "waqi_token" in os.environ:
            self.waqi_token = str(os.environ["waqi_token"])
        # if both not found, error
        else:
            raise AttributeError("No waqi.com token provided")
        
    ''' Get average pm2.5 from all stations in area
    @param: sampling_count:float: number of times to sample per minute (count/minute), suggested sampling count: <=6/min
    @param: sampling_time:float: time the sampling will last in minute (minute), suggested time: <10 min
    '''
    def get_average_pm25(self, sampling_count=5, sampling_time=1):
        # get all average for each station
        station_average_data = self.get_average_pm25_per_station(sampling_count, sampling_time)
        pm25_net = 0
        
        # calculate the net pm2.5 from all station
        for station_name in station_average_data:
            pm25_net += station_average_data[station_name]
            
        # average out 
        pm25_avg = pm25_net / len(station_average_data)
        
        return pm25_avg
    
    ''' Get average pm2.5 for each station in the area
    @param sampling_count:float: number of times to sample per minute (count/minute), suggested sampling count: <=6/min
    @param sampling_time:float: time the sampling will last in minute (minute), suggested time: <10 min
    @param get_result_format:str: what to use as result dict key, name = station name, id = station id
    @return dict of (str:float): for each station in area, return the average pm25 collected
    '''
    def get_average_pm25_per_station(self, sampling_count=5, sampling_time=1, get_result_format="name"):
        if sampling_count <= 0:
            raise AttributeError("Cannot process negative or zero sampling count")
        if sampling_time <= 0:
            raise AttributeError("Cannot process negative or zero sampling time")
        
        #get stations based on location region specified
        station_ids = self.get_station_uids(lat1, lng1, lat2, lng2)
        station_names = self.get_station_names(lat1, lng1, lat2, lng2) # this is added for readability of result
        
        #station ID is a better indication of station globally
        pm25_per_station = {}
        request_per_station = {}
        
        # counter to calculate max fail
        fail_count = 0
        
        #calculate total number of times sampling, round this to get integer
        total_sample_number = round(sampling_count * sampling_time) if total_sample_number >= 1 else 1
        
        # initialize station dict
        for station in station_ids:
            pm25_per_station[station] = 0
            request_per_station[station] = 0

        #sampling afterword
        for _ in range(total_sample_number):
            time.sleep(60 / sampling_time)
            for station in station_ids:
                try:
                    pm25_per_station[station] += self.get_pm25(station)
                    request_per_station[station] += 1
                except Exception:
                    fail_count += 1
                    print(f"A request to station {station} failed")
                    # if too many request failed, throw warning
                    if fail_count >= total_sample_number * len(station_ids) / 100:
                        fail_count = -total_sample_number * len(station_ids) # larger than total request number so Warning never triggers again
                        raise Warning("Too many failed requests, upstream service may not be functioning correctly")
                    
                    
        #place data in map for return 
        if get_result_format.lower == "id":
            station_average_data = dict(zip(station_ids, pm25_per_station))
        else:
            station_average_data = dict(zip(station_names, pm25_per_station))
        
        return station_average_data

    '''search for all monitor station in defined region
    @return: Array of station ID in region (using ID instead of name as search by stations do not return city name needed for city feed
    '''
    def get_station_uids(self):
        response = requests.get((f"https://api.waqi.info//map/bounds?token={self.waqi_token}&latlng=" + self.lat1 + "," + self.lng1 + "," + self.lat2 + "," + self.lng2))
        stationInArea = json.loads(response.text)
        stations = []
        for x in stationInArea["data"]:
            stations.append(x["uid"])
        return stations

    '''search for all monitor station in defined region
    @return: list: station name for printing
    '''
    def get_station_names(self):
        response = requests.get((f"https://api.waqi.info//map/bounds?token={self.waqi_token}&latlng=" + self.lat1 + "," + self.lng1 + "," + self.lat2 + "," + self.lng2))
        stationInArea = json.loads(response.text)
        station_names = []
        for x in stationInArea["data"]:
            station_names.append(x["station"]["name"])
        return station_names

    '''Given stationID, return current pm2.5 
    @param stationID: id of the station to query
    @return: current pm2.5 data of station
    '''
    def get_pm25(self, stationID):
        response = requests.get(f"https://api.waqi.info/feed/@{str(stationID)}/?token={self.waqi_token}")
        stationData = json.loads(response.text)
        return stationData["data"]["iaqi"]["pm25"]["v"]


if __name__ == "__main__":
    # Checking python parameter when file is directly provoked
    if len(sys.argv) <= 4:
        raise AttributeError("Number of argument under requirement, make sure to provide all 2 coordinates")
    lat1 = sys.argv[1]
    lng1 = sys.argv[2]
    lat2 = sys.argv[3]
    lng2 = sys.argv[4]
    sampling_count = sys.argv[5] if len(sys.argv) >= 6 else - 1
    sampling_time = sys.argv[6] if len(sys.argv) >= 7 else - 1
    if len(sys.argv) >= 8:
        raise Warning("Input argument number beyond needed, extra argument ignored.")
    
    # Pass result to calculator class
    param_calculator = PM25_Calculator(lat1, lng1, lat2, lng2)
    pm25_avg = param_calculator.get_average_pm25(sampling_count, sampling_time)
    print(f"---Average PM 2.5 for all stations in region: {pm25_avg}---")