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
import json


urlGeneral = "https://api.covid19india.org/data.json"
urlConfirmed = "http://api.covid19india.org/states_daily_csv/confirmed.csv"
urlDeaths = "https://api.covid19india.org/states_daily_csv/deceased.csv"
urlStatesDailyJSON = "https://api.covid19india.org/states_daily.json"


def get_data(ts, theUrl):
    tFile = "data/{}-covid19india_org-{}".format(ts, os.path.basename(theUrl))
    if os.path.exists(tFile) and (os.path.getsize(tFile)>128):
        print("INFO:{}:already downloaded".format(tFile))
        return tFile
    print("INFO:{}:downloading...".format(tFile))
    tCmd = [ "wget", theUrl, "--output-document={}"]
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


def extract_data_csv(tFile):
    # Instead of skipping the header line, load it has the names list
    data = np.genfromtxt(tFile, delimiter=',', skip_header=0, names=True, converters={0: date2float})
    legends = data.dtype.names[:-1]
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


def extract_data_json(tFile):
    f = open(tFile)
    dD = json.load(f)
    nda = np.zeros((len(dD['tested']), 3))
    for i in range(len(dD['tested'])):
        cur = dD['tested'][i]
        d,m,y = cur['updatetimestamp'].split(' ')[0].split('/')
        cDate = int(y)*10000 + int(m)*100 + int(d)
        nda[i,0] += cDate
        try:
            cPosCases = int(cur['totalpositivecases'])
        except ValueError:
            cPosCases = 0
        nda[i,1] += cPosCases
        try:
            cSamplesTested = int(cur['totalsamplestested'])
        except ValueError:
            cSamplesTested = 0
        nda[i,2] += cSamplesTested
    return nda, ['date', 'PosCases', 'Tested']


def extract_data(tFile, fileType = "csv"):
    if fileType == "csv":
        return extract_data_csv(tFile)
    elif fileType == "json":
        return extract_data_json(tFile)
    else:
        print("Unknown fileType[{}]".format(fileType))
        exit(1)


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


def _plot_data_selective(axes, theData, theSelection, sTitle, theLegends=None):
    axes.plot(theData[:,theSelection[0]])
    axes.set_title(sTitle)
    axes.set_xticks(np.arange(0,theData.shape[0],7))
    axes.set_xticklabels(theData[0::7,0].astype(np.int))
    if theLegends != None:
        axes.legend(np.array(theLegends)[theSelection[0]])


def plot_data_confirmed(theData, theLegends, theFile):

    pltRows = 2
    pltCols = 2
    fig, axes = plt.subplots(pltRows, pltCols)
    fig.set_figwidth(pltCols*9)
    fig.set_figheight(pltRows*6)

    theDates = theData[:,0]
    theDataCum = np.cumsum(theData, axis=0)
    the85Percentile = np.percentile(theDataCum[-1:,2:], 85, axis=1)
    theDataCum[:,0] = theDates
    print("theDataCumLatest", theDataCum[-1:,:].astype(np.int))
    print("the85Percentile", the85Percentile)
    # Plot only the states with more cases
    theSevereStates = theDataCum[-1:,:] > the85Percentile[0]
    theSevereStates[0,0] = False
    theSevereStates[0,1] = False
    print("SevereStates", theSevereStates)
    print("SevereStates",  np.array(theLegends)[theSevereStates[0]])
    _plot_data_selective(axes[0,0], theData, theSevereStates, "MoreCasesStates,85p, Cases/Day", theLegends)
    _plot_data_selective(axes[0,1], theDataCum, theSevereStates, "MoreCasesStates,85p, CasesCumu", theLegends)

    tWeight = np.ones(7)*1/7
    theDataConv = np.zeros((theData.shape[0]-6,theData.shape[1]))
    for i in range(1,theData.shape[1]):
        theDataConv[:,i] = np.convolve(theData[:,i], tWeight, 'valid')
    theDataConv[:,0] = list(range(theDataConv.shape[0]))
    _plot_data_selective(axes[1,0], theDataConv, theSevereStates, "MoreCasesStates,85p, Cases/Day,MovAvg", theLegends)

    # The boxplot of all states
    axes[1,1].boxplot(theData[:,2:],labels=theLegends[2:])


    fig.text(0.01, 0.002, "File:{}:DataDate:{}, hkvc".format(theFile, int(theDates[-1])))
    fig.set_tight_layout(True)
    fig.savefig("/tmp/{}.svg".format(os.path.basename(theFile)))
    plt.show()


def plot_data_general(theData, theLegend, theFile):

    pltRows = 2
    pltCols = 2
    fig, axes = plt.subplots(pltRows, pltCols)
    fig.set_figwidth(pltCols*9)
    fig.set_figheight(pltRows*6)

    theDates = theData[:,0]
    axes[0,0].plot(theData[:,1])
    axes[0,0].set_title("Cases")
    axes[0,1].plot(theData[:,2])
    axes[0,1].set_title("Tests")
    print("Cases:mean={}:std={}", np.mean(theData[:,1]), np.std(theData[:,1]))
    print("Tests:mean={}:std={}", np.mean(theData[:,2]), np.std(theData[:,2]))
    axes[1,0].plot(theData[:,1]/np.mean(theData[:,1]), label="CasesRel")
    axes[1,0].plot(theData[:,2]/np.mean(theData[:,2]), label="TestsRel")
    axes[1,0].legend()

    fig.text(0.01, 0.002, "File:{}:DataDate:{}, hkvc".format(theFile, int(theDates[-1])))
    fig.set_tight_layout(True)
    fig.savefig("/tmp/{}.svg".format(os.path.basename(theFile)))
    plt.show()



ts = time.gmtime()
ts = "{:04}{:02}{:02}".format(ts.tm_year, ts.tm_mon, ts.tm_mday)
print(ts)

theFileC = None
theFile = None
theFileG = None
if len(sys.argv) == 1:
    theFileC=get_data(ts, urlConfirmed)
    theFileG = get_data(ts, urlGeneral)
else:
    theFile = sys.argv[1]

for tFile in [theFile, theFileC, theFileG]:
    if tFile == None:
        continue
    tExt = tFile.rsplit('.',1)[1]
    theData, theLegends = extract_data(tFile, tExt)
    print(theLegends)
    if tExt == "csv":
        plot_data_confirmed(theData, theLegends, tFile)
    if tExt == "json":
        plot_data_general(theData, theLegends, tFile)


