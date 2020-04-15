#!/usr/bin/env python3
# Look at Data from http://api.covid19india.org/
# v20200415IST1950, HanishKVC
#

import sys
import os
import time
import subprocess
import numpy as np


urlConfirmed = "http://api.covid19india.org/states_daily_csv/confirmed.csv"
urlDeaths = "https://api.covid19india.org/states_daily_csv/deceased.csv"


def get_data(ts):
    tFile = "data/covid19india_org-{}".format(ts)
    if os.path.exists(tFile):
        print("INFO:{}:already downloaded".format(tFile))
        return tFile
    print("INFO:{}:downloading...".format(tFile))
    tCmd = [ "wget", urlConfirmed, "--output-document={}"]
    tCmd[2] = tCmd[2].format(tFile)
    subprocess.call(tCmd)
    return tFile


def extract_data(tFile):
    data = np.loadtxt(tFile, delimiter=',', skiprows=1)
    print(data)


if len(sys.argv) == 1:
    ts = time.gmtime()
    ts = "{:04}{:02}{:02}".format(ts.tm_year, ts.tm_mon, ts.tm_mday)
    print(ts)
    theFile=get_data(ts)
else:
    theFile = sys.argv[1]

extract_data(theFile)


