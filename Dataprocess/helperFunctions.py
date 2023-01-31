import sys
import logging
import os
import json
from dotenv import load_dotenv
from datetime import datetime


def setup():
  load_dotenv()

  logging.basicConfig(
    format=f'%(asctime)s %(levelname)-8s %(message)s ',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
    logging.StreamHandler(sys.stdout)
    ])
    



def translateNumToScenario(number):
    if  ( number == "1" or number == 1):
        return "01 Norm-Norm"
    elif( number == "2" or number == 2):
        return "02 TorN-TorN"
    elif( number == "3" or number == 3):
        return "03 TorE-TorE"
    elif( number == "4" or number == 4):
        return "04 TorS-TorS"
    elif( number == "5" or number == 5):
        return "05 Loki-Loki"

    elif( number == "6" or number == 6):
        return "06 Norm-TorN"
    elif( number == "7" or number == 7):
        return "07 TorN-Norm"
    elif( number == "8" or number == 8):
        return "08 Norm-TorE"
    elif( number == "9" or number == 9):
        return "09 TorE-Norm"
    elif( number == "10" or number == 10):
        return "10 Norm-TorS"
    elif( number == "11" or number == 11):
        return "11 TorS-Norm"
    elif( number == "12" or number == 12):
        return "12 Norm-Loki"
    elif( number == "13" or number == 13):
        return "13 Loki-Norm"

    elif( number == "14" or number == 14):
        return "14 TorN-TorE"
    elif( number == "15" or number == 15):
        return "15 TorE-TorN"
    elif( number == "16" or number == 16):
        return "16 TorN-TorS"
    elif( number == "17" or number == 17):
        return "17 TorS-TorN"
    elif( number == "18" or number == 18):
        return "18 TorE-TorS"
    elif( number == "19" or number == 19):
        return "19 TorS-TorE"
    else:
        return "UNKNOWN!"

def getScenarioLabels(order) -> list[str]:
    labels = []
    for i in order:
        labels.append(translateNumToScenario(str(i)))
    return labels



c1 = "c1-Normal"
c2 = "c2-TorNormal"
c3 = "c3-TorEurope"
c4 = "c4-TorScandinavia"
c5 = "c5-I2P"
c6 = "c6-Lokinet"
d1 = "d1-Normal"
d2 = "d2-TorNormal"
d3 = "d3-TorEurope"
d4 = "d4-TorScandinavia"
d5 = "d5-I2P"
d6 = "d6-Lokinet"



scenarios = [
  {
    "scenario": 1,
    "alice": c1,
    "bob": d1
  },{
    "scenario": 2,
    "alice": c2,
    "bob": d2
  },{
    "scenario": 3,
    "alice": c3,
    "bob": d3
  },{
    "scenario": 4,
    "alice": c4,
    "bob": d4
  },{
    "scenario": 5,
    "alice": c6,
    "bob": d6
  },
  
  {
    "scenario": 6,
    "alice": c1,
    "bob": d2
  },{
    "scenario": 7,
    "alice": c2,
    "bob": d1
  },{
    "scenario": 8,
    "alice": c1,
    "bob": d3
  },{
    "scenario": 9,
    "alice": c3,
    "bob": d1
  },{
    "scenario": 10,
    "alice": c1,
    "bob": d4
  },{
    "scenario": 11,
    "alice": c4,
    "bob": d1
  },{
    "scenario": 12,
    "alice": c1,
    "bob": d6
  },{
    "scenario": 13,
    "alice": c6,
    "bob": d1
  },
  
  {
    "scenario": 14,
    "alice": c2,
    "bob": d3
  },{
    "scenario": 15,
    "alice": c3,
    "bob": d2
  },{
    "scenario": 16,
    "alice": c2,
    "bob": d4
  },{
    "scenario": 17,
    "alice": c4,
    "bob": d2
  },{
    "scenario": 18,
    "alice": c3,
    "bob": d4
  },{
    "scenario": 19,
    "alice": c4,
    "bob": d3
  }
]