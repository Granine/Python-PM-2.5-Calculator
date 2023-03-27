import sys
import os
sys.path.append(f"{__file__}/../..")
import pm25
from unittest import mock

def random_area_1():
    # A random area with stations
    return (39,116,-40,116.01)

@mock.patch.dict(os.environ, {"waqi_token": "DUMMY"})
def test_pm_25_class_initialization():
    '''Basic test to ensure class can be initialized
    '''
    os.environ["waqi_token"] = "DUMMY"
    pm25_calc = pm25.PM25_Calculator(*random_area_1())
    assert type(pm25_calc) == pm25.PM25_Calculator

@mock.patch.dict(os.environ, {"waqi_token": "DUMMY"})
def test_pm_25_class_no_token():
    '''Make sure class fails initialization if no token detected
    '''
    save_token = ""
    if "waqi_token" in os.environ.keys(): 
        save_token = os.environ["waqi_token"]
        del(os.environ["waqi_token"])
    try:
        pm25_calc = pm25.PM25_Calculator(*random_area_1())
    except AttributeError:
        pass
    else:
        assert "Class did not error out without token" == 0
    if save_token:
        os.environ["waqi_token"] = save_token
        
def test_pm_25_general():
    '''General pm25 test
    '''
    if "waqi_token" not in os.environ: 
        raise Warning("waqi_token not set in environmental variable")
    pm25_calc = pm25.PM25_Calculator(*random_area_1())
    assert type(pm25_calc) == pm25.PM25_Calculator
    assert type(pm25_calc.get_average_pm25(1, 0))