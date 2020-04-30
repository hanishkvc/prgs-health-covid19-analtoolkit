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
    return dsEU, dsC19In


def plot_simple():
    fig, axes = ap.subplots(plt,4,2)
    iCur = 0
    sGlobalMsg = ""
    for ds in [ dsC19In, dsEU ]:
        ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr[2:])
        ap.plot(axes[0,iCur], "raw", numXTicks=4, xtickMultOf=7)
        ap.calc_rel2mean()
        ap.plot(axes[1,iCur], "raw.rel2mean")
        ap.calc_rel2sum()
        ap.plot(axes[2,iCur], "raw.rel2sum")
        ap.calc_movavg()
        selCols, selPers = ap.selcols_percentiles("raw.movavg")
        ap.plot(axes[3,iCur], "raw.movavg", plotSelCols=selCols)
        sGlobalMsg += " {}:DataDate:{}-{};".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCur += 1
    save_fig(fig, sGlobalMsg)


def plot_sel():
    fig, axes = ap.subplots(plt,3,2)
    iCur = 0
    sGlobalMsg = ""
    for ds in [ dsC19In, dsEU ]:
        dprint("DBUG:Main:plot_sel:hdr-type:%s" %(type(ds.hdr[5])))
        ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr[2:])
        ap.plot(axes[0,iCur], "raw", numXTicks=4, xtickMultOf=7)
        ap.calc_movavg()
        """
        selCols, selPers = ap.selcols_percentiles("raw.movavg", selPers=[0,15])
        ap.plot(axes[1,iCur], "raw.movavg", plotSelCols=selCols, plotLegend=True)
        """
        selCols, selPers = ap.selcols_percentiles("raw.movavg", topN=15)
        ap.plot(axes[1,iCur], "raw.movavg", plotSelCols=selCols, plotLegend=True, yscale="log")
        ap.boxplot(axes[2,iCur], "raw", plotSelCols=selCols, bInsetBoxPlot=True)
        sGlobalMsg += " {}:DataDate:{}-{};".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCur += 1
    save_fig(fig, sGlobalMsg)


def save_fig(fig, sMsg):
    sMsg += " hkvc"
    fig.text(0.01, 0.002, sMsg)
    fig.set_tight_layout(True)
    tFName = sMsg.replace(";","_N_").replace(" ","_")
    fig.savefig("/tmp/{}.svg".format(tFName))
    plt.show()


dsEU, dsC19In = fetch()
ap = analplot.AnalPlot()
plot_simple()
plot_sel()

# vim: set softtabstop=4 expandtab shiftwidth=4: #
