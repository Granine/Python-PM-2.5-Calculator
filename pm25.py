'''
Date: April 26, 2022
Auther: Guan Zheng Huang
Task number: NA
Task name: OSENSA AQI Python CMD Line Assignment
Edit: NA
Goal: calculate average of air pollutant PM2.5 in a specified region
'''

'''
Uncertainty: 
time: Based on my review of the documentiation for the API there does not seem to be a "history air quality" look up feature
    So I assumed the averaging starts after program starts.
definition of station: according to requirement "Print PM2.5 sampled value for each station.". However
    what identifies a station is not stated, I implemented the program using name for readability.
'''

'''
known issues:
if any station/system fails at anytime, the entire averaging process will fail
because of API access time, access time will be longer than expected (eg: if sampling every 10 second, 
    actual time is 10 + API time), this can be resolved by using system clock or multithreading.
    However, this first requires constant for loop (power intensive), latter is too complicated for the task.
sampling time and rate can be float but must be of a reasonable range (this depend on device so not checked in code)
    suggested time: 0~10
    suggested rate: 0.1~16
'''

'''
sample run command:
sample 8 times per minuit for 2 minuit (3 station)
    python pm25.py 39 116 41 116.04 2 8
sample 1 times per minuit for 3 minuit
    python pm25.py 39 116 41 116.04 3
sample 1 times per minuit for 5 minuit
    python pm25.py 39 116 41 116.04 

'''

import sys
import json
import requests
import time

debug = False

#@param: None (argv from system)
#@return: None
#require: requires input parameter to be between 5 and 7
#require: lat and lng for first point in arg 1, 2, float
#require: lat and lng for second point in arg 3, 4, float
#require: total time to average in minuit in arg 5, positive float
#require: number of times to sample per minuit in arg 6, positive float
#effect: result is printed
#calculate average of air pollutant PM2.5 over n minutes for each station and average of all station in a specified region
def pm25Calc():
    lat1 = sys.argv[1]
    lng1 = sys.argv[2]
    lat2 = sys.argv[3]
    lng2 = sys.argv[4]
    
    #check if inputs are valid
    if (len(sys.argv)==5):
        samplingTime = 5
        samplingRate = 1
    elif (len(sys.argv)==6):
        samplingTime = float(sys.argv[5])
        samplingRate = 1
    elif (len(sys.argv)==7):
        samplingTime = float(sys.argv[5])
        samplingRate = float(sys.argv[6])
    else:
        print("invalid input parameter number, there must be between 5 and 7 parameters")
        exit()

    #get station based on location region specified
    stations = getStations(lat1, lng1, lat2, lng2)
    stationName = getStationsName(lat1, lng1, lat2, lng2) # this is added for readability of result
    #station ID is a better indication of station globally
    pm25EachStation = []

    #calculate total number of times sampling, round this to get integer
    totalSampleNumber = int(samplingTime*samplingRate) 
    #should sample at least once
    if totalSampleNumber<1: totalSampleNumber = 1

    #first sample and create array to record sample for each station
    for station in stations:
        pm25EachStation.append(getPM25(station)/totalSampleNumber)
    if (debug): print (pm25EachStation)

    #sampling afterword
    for samplingCounter in range(totalSampleNumber-1):
        #see above "known issues" for reasons to use sleep
        time.sleep(60/samplingRate)
        for station in range(len(stations)):
            pm25EachStation[station]+=getPM25(station)/totalSampleNumber
        if (debug): print (pm25EachStation)

    #printing
    pm25avg = sum(pm25EachStation)/len(pm25EachStation)
    
    #place data in map so it follows 
    stationData = dict(zip(stationName, pm25EachStation))
    print("PM 2.5 for each station:")
    for stationCount in range(len(stationName)):
        print(list(stationData.items())[stationCount])

    #if consistant format as API is needed
    #print(stationData)
    print("Average PM 2.5 for all stations in reigion: ", pm25avg)

#@param: lat1/lat2: lattitude of region to search
#@param: lng1/lng2: longtitude of region to search
#@return: Array of station ID in reigion (using ID instead of name as searcg by stations do not return city name needed for city feed
#search for all monitor station in defined region
def getStations(lat1, lng1, lat2, lng2):
    response = requests.get(("https://api.waqi.info//map/bounds?token=a680e3cd0496283661a9ab60a52c5a81e0e9c807&latlng="+ lat1 +","+ lng1 +","+ lat2 + "," + lng2))
    stationInArea = json.loads(response.text)
    stations = []
    for x in stationInArea["data"]:
        stations.append(x["uid"])
    if (debug): print(stations)
    return stations

#@param: lat1/lat2: lattitude of region to search
#@param: lng1/lng2: longtitude of region to search
#@return: station name for printing
#search for all monitor station in defined region
def getStationsName(lat1, lng1, lat2, lng2):
    response = requests.get(("https://api.waqi.info//map/bounds?token=a680e3cd0496283661a9ab60a52c5a81e0e9c807&latlng="+ lat1 +","+ lng1 +","+ lat2 + "," + lng2))
    stationInArea = json.loads(response.text)
    stations = []
    for x in stationInArea["data"]:
        stations.append(x["station"]["name"])
    if (debug): print(stations)
    return stations

#@param stationID: id of the station to search
#@return: station test of pm2.5 data
def getPM25(stationID):
    response = requests.get("https://api.waqi.info/feed/@"+str(stationID)+"/?token=a680e3cd0496283661a9ab60a52c5a81e0e9c807")
    stationData = json.loads(response.text)
    return stationData["data"]["iaqi"]["pm25"]["v"]

if __name__ == "__main__":
    pm25Calc()