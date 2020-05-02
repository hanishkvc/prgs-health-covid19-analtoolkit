#!/usr/bin/env python3
# Covid19 AnalToolkit
# v20200502IST1808, HanishKVC
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
        ap.new_dataset()
        ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr[2:], dataKey="cases/day")
        ap.plot(axes[0,iCur], "cases/day", numXTicks=4, xtickMultOf=7, title="%s-Cases/Day"%(ds.name))
        ap.calc_rel2mean("cases/day")
        ap.plot(axes[1,iCur], "cases/day.rel2mean", title="%s-Cases/Day_Rel2Mean"%(ds.name))
        ap.calc_rel2sum("cases/day")
        ap.plot(axes[2,iCur], "cases/day.rel2sum", title="%s-Cases/Day_Rel2Sum"%(ds.name))
        ap.calc_movavg("cases/day")
        selCols, selPers = ap.selcols_percentiles("cases/day.movavg")
        ap.plot(axes[3,iCur], "cases/day.movavg", plotSelCols=selCols, title="%s-Cases/Day_MovAvg"%(ds.name))
        sGlobalMsg += "{}-Data-{}_{}--".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCur += 1
    save_fig(fig, sGlobalMsg)


def plot_diffdata(ds, ap, axes, iARow, iACol, dataKey="cases/day", sBaseDataMsg="Cases/Day"):
    ap.calc_diff(dataKey)
    ap.calc_movavg_ex(dataKey="%s.diff"%(dataKey), times=2)
    ap.calc_movavg_ex(dataKey="%s.diff"%(dataKey), times=3)
    selCols, selPers = ap.selcols_percentiles("%s.diff.movavgT2"%(dataKey), topN=8)
    ap.plot(axes[iARow,iACol], "%s.diff.movavgT3"%(dataKey), plotSelCols=selCols, plotLegend=True,
                title="%s-DiffOf%s_MovAvgT3-DiffMovAvgT2Top8"%(ds.name, sBaseDataMsg))
    inset = axes[iARow,iACol].inset_axes([0.13,0.55,0.64,0.4])
    ap.plot(inset, "%s.diff"%(dataKey), plotSelCols=selCols, plotLegend=None, bTranslucent=True,
                title="%s-DiffOf%s-DiffMovAvgT2Top8"%(ds.name, sBaseDataMsg))
    ap.calc_rel2sum(dataKey)
    ap.calc_movavg_ex(dataKey="%s.rel2sum"%(dataKey), times=2)
    ap.plot(axes[iARow+1,iACol], "%s.rel2sum.movavgT2"%(dataKey), plotSelCols=selCols, plotLegend=True,
                title="%s-MovAvgT2OfRel2SumOf%s-DiffMovAvgT2Top8"%(ds.name, sBaseDataMsg))
    ap.plotxy(axes[iARow+2,iACol], "%s.movavg"%(dataKey), "%s.diff.movavgT2"%(dataKey), plotSelCols=selCols, plotLegend=True)
    selCols, selPers = ap.selcols_percentiles("%s.diff.movavgT2"%(dataKey), topN=25, bSelInclusive=True)
    ap.plotxy(axes[iARow+3,iACol], "%s.movavg"%(dataKey), "%s.diff.movavgT2"%(dataKey), plotSelCols=selCols,
                title="%s-__AUTO__~Top25(diff.movavgT2)"%(ds.name), xscale="log", yscale="log", plotLegend=True)
    ap.calc_cumsum(dataKey)
    selCols, selPers = ap.selcols_percentiles("%s.cumsum"%(dataKey), topN=25, bSelInclusive=True)
    ap.plotxy(axes[iARow+4,iACol], "%s.cumsum"%(dataKey), "%s.movavg"%(dataKey), plotSelCols=selCols,
                title="%s-__AUTO__~Top25(cumsum)"%(ds.name), xscale="log", yscale="log", plotLegend=True)


def plot_sel(allDS):
    fig, axes = ap.subplots(plt,8,2)
    iCur = 0
    sGlobalMsg = ""
    for ds in allDS:
        ap.new_dataset()
        dprint("DBUG:Main:plot_sel:hdr-type:%s" %(type(ds.hdr[-2])))
        # The Raw data
        ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr[2:], dataKey="cases/day")
        ap.plot(axes[0,iCur], "cases/day", numXTicks=4, xtickMultOf=7, title="%s-Cases/Day-All"%(ds.name))
        # The moving avg
        ap.calc_movavg("cases/day")
        """
        selCols, selPers = ap.selcols_percentiles("cases/day.movavg", selPers=[0,15])
        ap.plot(axes[1,iCur], "cases/day.movavg", plotSelCols=selCols, plotLegend=True)
        """
        selCols, selPers = ap.selcols_percentiles("cases/day.movavg", topN=12)
        yscale = "log"
        yscale = None
        ap.plot(axes[1,iCur], "cases/day.movavg", plotSelCols=selCols, plotLegend=True, yscale=yscale, title="%s-Cases/Day_MovAvg-MovAvgTop12"%(ds.name))
        # Boxplot Raw data
        selCols, selPers = ap.selcols_percentiles("cases/day.movavg", topN=15)
        ap.boxplot(axes[2,iCur], "cases/day", plotSelCols=selCols, bInsetBoxPlot=True, title="%s-Cases/Day-MovAvgTop15"%(ds.name))
        # Diff of Raw data
        plot_diffdata(ds, ap, axes, 3, iCur)
        #ap.calc_rel2sum()
        #plot_diffdata(ds, ap, axes, 4, iCur, dataKey="cases/day.rel2sum", sBaseDataMsg="Rel2SumOfCases/Day")
        sGlobalMsg += "{}-Data-{}_{}--".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCur += 1
    save_fig(fig, sGlobalMsg)


def save_fig(fig, sMsg):
    sMsg += "-hkvc"
    fig.text(0.01, 0.002, sMsg)
    fig.set_tight_layout(True)
    tFName = sMsg.replace(";","_N_").replace(" ","_")
    fig.savefig("/tmp/{}.svg".format(tFName))
    fig.savefig("/tmp/{}.png".format(tFName))
    plt.show()


def load_fromargs(args):
    iArg = 1
    dsAll = []
    while iArg < len(args):
        if args[iArg] == "--cov19in":
            iArg += 1
            ds = dsrc.Cov19InDataSrc()
            ds.load_data(args[iArg])
            iArg += 1
            dsAll.append(ds)
        elif args[iArg] == "--euworld":
            iArg += 1
            ds = dsrc.EUWorldDataSrc()
            ds.load_data(args[iArg])
            iArg += 1
            dsAll.append(ds)
        else:
            print("ERRR:Main:load_fromargs:UnknownArg:%s"%(args[iArg]))
            iArg += 1
    return dsAll



if len(sys.argv) <= 1:
    allDS = fetch()
else:
    allDS = load_fromargs(sys.argv)

ap = analplot.AnalPlot()
#plot_simple(allDS)
plot_sel(allDS)

# vim: set softtabstop=4 expandtab shiftwidth=4: #
