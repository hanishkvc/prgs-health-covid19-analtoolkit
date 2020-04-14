#!/usr/bin/env python3

import sys
import os
import subprocess
import time


def get_data(ts):
    tFile = "{}.html".format(ts)
    if os.path.exists(tFile):
        print("WARN:get_data:{} already exists".format(tFile))
        return tFile
    tCmd = [ "wget", "https://www.mygov.in/corona-data/covid19-statewise-status", "--output-document={}"]
    tCmd[2] = tCmd[2].format(tFile)
    print(tCmd)
    subprocess.call(tCmd)
    return tFile


ts = time.gmtime()
ts = "{:04}{:02}{:02}GMT{:02}".format(ts.tm_year, ts.tm_mon, ts.tm_mday, ts.tm_hour)
theFile=get_data(ts)

