#!/usr/bin/env python3
# Look at Data from http://api.covid19india.org/
# v20200415IST1950, HanishKVC
#

import sys
import os
import time
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import calendar


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


def date2float(sDate):
    if sDate == b'1': # Had to use to skip the genfromtxt names=True related line
        return "Date"
    sDate = sDate.decode('utf-8')
    sDate = sDate.split('-')
    iDate = (int(sDate[2])+2000)*10000
    iDate += list(calendar.month_abbr).index(sDate[1])*100
    iDate += int(sDate[0])
    return float(iDate)


def extract_data(tFile):
    # Instead of skipping the header line, load it has the names list
    data = np.genfromtxt(tFile, delimiter=',', skip_header=0, names=True, converters={0: date2float})
    legends = data.dtype.names
    # Needed to convert from the numpy.void rows to a proper nd-array
    data = np.array(data.tolist())
    # Skip the last column, which is invalid.
    data = data[:,0:-1]
    #data[12,1] = np.nan # For testing below logic to fix missing values is fine
    nans = np.argwhere(np.isnan(data))
    data[np.isnan(data)] = 0
    for i in nans:
        iS = i[0]-3
        if (iS < 0):
            iS = 0
        iE = i[0]+3+1
        if (iE > data.shape[0]):
            iE = data.shape[0]
        print("WARN:extract_data:fix_nan:at={}:using={}-{}".format(i, iS, iE))
        print("\tIN:{}".format(data[iS:iE,i[1]]))
        tWeights = np.ones(iE-iS)*1/6
        data[i] = np.sum(data[iS:iE,i[1]]*tWeights)
        print("\tNEW:{}".format(data[iS:iE,i[1]]))
    return data, legends


def _plot_data(axes, theData, sTitle, theLegends=None):
    #for i in range(1,theData.shape[1]):
    #    plt.plot(theData[:,i])
    # Skip 0th Col the Date and
    # Skip 1st Col the Total
    axes.plot(theData[:,2:])
    axes.set_title(sTitle)
    axes.set_xticks(np.arange(0,theData.shape[0],7))
    axes.set_xticklabels(theData[0::7,0].astype(np.int))
    if theLegends != None:
        axes.legend(theLegends[2:8])


def plot_data(theData, theLegends):

    fig, axes = plt.subplots(2,2)
    _plot_data(axes[0,0], theData, "Cases/Day", theLegends)

    theDates = theData[:,0]
    theDataCum = np.cumsum(theData, axis=0)
    theDataCum[:,0] = theDates
    _plot_data(axes[0,1], theDataCum, "CumuCases")

    tWeight = np.ones(7)*1/7
    theDataConv = np.zeros((theData.shape[0]-6,theData.shape[1]))
    for i in range(1,theData.shape[1]):
        theDataConv[:,i] = np.convolve(theData[:,i], tWeight, 'valid')
    theDataConv[:,0] = list(range(theDataConv.shape[0]))
    _plot_data(axes[1,0], theDataConv, "Cases/Day,MovAvg")

    print(theData.shape, len(theLegends))
    axes[1,1].boxplot(theData[:,2:],labels=theLegends[2:-1])
    plt.show()



if len(sys.argv) == 1:
    ts = time.gmtime()
    ts = "{:04}{:02}{:02}".format(ts.tm_year, ts.tm_mon, ts.tm_mday)
    print(ts)
    theFile=get_data(ts)
else:
    theFile = sys.argv[1]

theData, theLegends = extract_data(theFile)
plot_data(theData, theLegends)

