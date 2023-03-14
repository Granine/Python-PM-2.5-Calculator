import sys
sys.path.append("../..")
import os
import pm25

def random_area_1():
    return (54, -354, 55, -355)

def test_pm_25_class_initialization():
    os.environ["waqi_token"] = "DUMMY"
    pm25_calc = pm25.PM25_Calculator(*random_area_1())
    print (type(pm25_calc))