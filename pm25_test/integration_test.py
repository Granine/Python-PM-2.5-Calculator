import sys
import os
sys.path.append(f"{__file__}/../..")
import pm25

def random_area_1():
    # A random area with stations
    return (54, -354, 55, -354.5)

def test_pm_25_class_initialization():
    '''Basic test to ensure class can be initialized
    '''
    os.environ["waqi_token"] = "DUMMY"
    pm25_calc = pm25.PM25_Calculator(*random_area_1())
    assert type(pm25_calc) == pm25.PM25_Calculator
    
def test_pm_25_class_no_token():
    '''Make sure class fails initialization if no token detected
    '''
    if "waqi_token" in os.environ.keys(): del(os.environ["waqi_token"])
    try:
        pm25_calc = pm25.PM25_Calculator(*random_area_1())
    except AttributeError:
        pass
    else:
        assert "Class did not error out without token" == 0
        
def test_pm_25_general():
    '''General pm25 test
    '''
    if "waqi_token" not in os.environ.keys(): 
        raise Warning("waqi_token not set in environmental variable")
    pm25_calc = pm25.PM25_Calculator(*random_area_1())
    assert type(pm25_calc) == pm25.PM25_Calculator
    assert type(pm25_calc.get_average_pm25(1, 0))