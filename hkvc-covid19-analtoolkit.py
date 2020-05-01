#!/usr/bin/env python3
# Covid19 AnalToolkit
# v20200430IST1746, HanishKVC
#

import sys
import datasrc as dsrc
import analplot
import matplotlib.pyplot as plt
import numpy as np
from helpers import *


def fetch():
    dsEU = dsrc.EUWorldDataSrc()
    dsC19In = dsrc.Cov19InDataSrc()
    for ds in [ dsC19In, dsEU ]:
        ds.fetch_data()
        ds.load_data()
    return [ dsEU, dsC19In ]


def plot_simple(allDS):
    fig, axes = ap.subplots(plt,4,2)
    iCur = 0
    sGlobalMsg = ""
    for ds in allDS:
        ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr[2:])
        ap.plot(axes[0,iCur], "raw", numXTicks=4, xtickMultOf=7, title="%s-Cases/Day"%(ds.name))
        ap.calc_rel2mean()
        ap.plot(axes[1,iCur], "raw.rel2mean", title="%s-Cases/Day_Rel2Mean"%(ds.name))
        ap.calc_rel2sum()
        ap.plot(axes[2,iCur], "raw.rel2sum", title="%s-Cases/Day_Rel2Sum"%(ds.name))
        ap.calc_movavg()
        selCols, selPers = ap.selcols_percentiles("raw.movavg")
        ap.plot(axes[3,iCur], "raw.movavg", plotSelCols=selCols, title="%s-Cases/Day_MovAvg"%(ds.name))
        sGlobalMsg += "{}-Data-{}_{}--".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCur += 1
    save_fig(fig, sGlobalMsg)


def plot_sel(allDS):
    fig, axes = ap.subplots(plt,4,2)
    iCur = 0
    sGlobalMsg = ""
    for ds in allDS:
        dprint("DBUG:Main:plot_sel:hdr-type:%s" %(type(ds.hdr[-2])))
        # The Raw data
        ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr[2:])
        ap.plot(axes[0,iCur], "raw", numXTicks=4, xtickMultOf=7, title="%s-Cases/Day-All"%(ds.name))
        # The moving avg
        ap.calc_movavg()
        """
        selCols, selPers = ap.selcols_percentiles("raw.movavg", selPers=[0,15])
        ap.plot(axes[1,iCur], "raw.movavg", plotSelCols=selCols, plotLegend=True)
        """
        selCols, selPers = ap.selcols_percentiles("raw.movavg", topN=12)
        yscale = "log"
        yscale = None
        ap.plot(axes[1,iCur], "raw.movavg", plotSelCols=selCols, plotLegend=True, yscale=yscale, title="%s-Cases/Day_MovAvg-MovAvgTop12"%(ds.name))
        # Boxplot Raw data
        selCols, selPers = ap.selcols_percentiles("raw.movavg", topN=15)
        ap.boxplot(axes[2,iCur], "raw", plotSelCols=selCols, bInsetBoxPlot=True, title="%s-Cases/Day-MovAvgTop15"%(ds.name))
        # Diff of Raw data
        ap.calc_diff()
        ap.calc_movavg_ex(dataSel="raw.diff", times=2)
        ap.calc_movavg_ex(dataSel="raw.diff", times=3)
        selCols, selPers = ap.selcols_percentiles("raw.diff.movavgT2", topN=8)
        ap.plot(axes[3,iCur], "raw.diff.movavgT3", plotSelCols=selCols, plotLegend=True, title="%s-DiffOfCases/Day_MovAvgT3-DiffMovAvgT2Top8"%(ds.name))
        inset = axes[3,iCur].inset_axes([0.13,0.55,0.64,0.4])
        ap.plot(inset, "raw.diff", plotSelCols=selCols, plotLegend=None, bTranslucent=True, title="%s-DiffOfCases/Day-DiffMovAvgT2Top8"%(ds.name))
        sGlobalMsg += "{}-Data-{}_{}--".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCur += 1
    save_fig(fig, sGlobalMsg)


def save_fig(fig, sMsg):
    sMsg += "-hkvc"
    fig.text(0.01, 0.002, sMsg)
    fig.set_tight_layout(True)
    tFName = sMsg.replace(";","_N_").replace(" ","_")
    fig.savefig("/tmp/{}.svg".format(tFName))
    plt.show()


def load_fromargs(args):
    iArg = 1
    dsAll = []
    while iArg < len(args):
        if args[iArg] == "--covid19in":
            iArg += 1
            ds = dsrc.Cov19InDataSrc()
            ds.load(args[iArg])
            iArg += 1
            dsAll.append(ds)
        elif args[iArg] == "--euworld":
            iArg += 1
            ds = dsrc.EUWorldDataSrc()
            ds.load(args[iArg])
            iArg += 1
            dsAll.append(ds)
        else:
            print("ERRR:Main:load_fromargs:UnknownArg:%s"%(args[iArg]))
    return dsAll



if len(sys.argv) <= 1:
    allDS = fetch()
else:
    allDS = load_fromargs(sys.argv)

ap = analplot.AnalPlot()
#plot_simple(allDS)
plot_sel(allDS)

# vim: set softtabstop=4 expandtab shiftwidth=4: #
