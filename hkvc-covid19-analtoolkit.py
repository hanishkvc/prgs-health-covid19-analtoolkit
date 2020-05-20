#!/usr/bin/env python3
# Covid19 AnalToolkit
# v20200502IST1808, HanishKVC
# GPL
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
    """ Plot few simple plots
        This uses the old call calc logics explicitly mechanism,
        which is no longer required, as AnalPlot handles calc
        automatically as required.
        """
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


def sel_cols(dataKey, topN, inSelIds, baseTilte, selTitle):
    if inSelIds == None:
        selCols, selPers = ap.selcols_percentiles(dataKey, topN=topN)
        theTitle = "%s-%sTop%d"%(baseTitle, selTitle, topN)
    else:
        selCols = ap.selcols_colhdr(inSelIds)
        theTitle = baseTitle+"-user"
    return selCols, theTitle


def plot_diffdata(ds, ap, axes, iARow, iACol, dataKey="cases/day", inSelIds=None):
    selCols, selPers = ap.selcols_percentiles("%s.diff.movavgT2"%(dataKey), topN=8)
    ap.plot(axes[iARow,iACol], "%s.diff.movavgT3"%(dataKey), plotSelCols=selCols, plotLegend=True,
                title="%s-__AUTO__-DiffMovAvgT2Top8"%(ds.name))
    inset = axes[iARow,iACol].inset_axes([0.13,0.55,0.64,0.4])
    ap.plot(inset, "%s.diff"%(dataKey), plotSelCols=selCols, plotLegend=None, bTranslucent=True,
                title="%s-__AUTO__-DiffMovAvgT2Top8"%(ds.name))
    ap.plot(axes[iARow+1,iACol], "%s.rel2sum.movavgT2"%(dataKey), plotSelCols=selCols, plotLegend=True,
                title="%s-__AUTO__-DiffMovAvgT2Top8"%(ds.name))
    selCols, selPers = ap.selcols_percentiles("%s.cumsum"%(dataKey), topN=25, bSelInclusive=True)
    ap.plotxy(axes[iARow+2,iACol], "%s.cumsum"%(dataKey), "%s.movavg"%(dataKey), plotSelCols=selCols,
                title="%s-__AUTO__~Top25(cumsum)"%(ds.name), xscale="log", yscale="log", plotLegend=True)
    inset = axes[iARow+2,iACol].inset_axes([0.6,0.10,0.4,0.4])
    selCols, selPers = ap.selcols_percentiles("%s.diff.movavgT2"%(dataKey), topN=8, bSelInclusive=True)
    analplot.textxy_spread("custom", 0.55)
    analplot.textxy_spread("default")
    ap.plotxy(inset, "%s.movavg"%(dataKey), "%s.diff.movavgT2"%(dataKey), plotSelCols=selCols, bTranslucent=True,
                title="Cases/Day mavgVSdiff(diffTop8)", xscale="log", yscale="log", plotLegend=True)
    analplot.textxy_spread("default")


def plot_sel(allDS, allSel):
    """ Plot a set of interesting/informative/... plots
        Uses the new auto calc as required functionality of AnalPlot
        """
    fig, axes = ap.subplots(plt,5,len(allDS))
    iCurDS = 0
    sGlobalMsg = ""
    for ds in allDS:
        ap.new_dataset()
        if ds.name in allSel:
            theSelIds = allSel[ds.name]
        else:
            theSelIds = None
        dprint("DBUG:Main:plot_sel:hdr-type:%s" %(type(ds.hdr[-2])))
        # The Raw data
        ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr[2:], dataKey="cases/day")
        # Plot moving avg and raw data (inset)
        topN=8
        theTitle = "%s-__AUTO__".format(ds.name)
        selCols, theTitle = sel_cols("cases/day.movavg", topN, theSelIds, theTitle, "movavg")
        ap.plot(axes[0,iCurDS], "cases/day.movavg", plotSelCols=selCols, plotLegend=True, title=theTitle, yscale="log")
        yscale = "log"
        yscale = None
        inset = axes[0,iCurDS].inset_axes([0.36,0.05,0.64,0.4])
        ap.plot(inset, "cases/day", plotSelCols=selCols, yscale=yscale, bTranslucent=True, numXTicks=4, xtickMultOf=7, title=theTitle)
        # Boxplot Raw data
        topN=20
        theTitle = "%s-__AUTO__".format(ds.name)
        selCols, theTitle = sel_cols("cases/day.movavg", topN, theSelIds, theTitle, "movavg")
        ap.boxplot(axes[1,iCurDS], "cases/day", plotSelCols=selCols, bInsetBoxPlot=True, title=theTitle)
        # Diff of Raw data and more
        plot_diffdata(ds, ap, axes, 2, iCurDS, "cases/day", theSelIds)
        sGlobalMsg += "{}-Data-{}_{}--".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCurDS += 1
    save_fig(fig, sGlobalMsg)


def save_fig(fig, sMsg):
    sMsg += "-hkvc"
    textMsg = sMsg + "; github.com/hanishkvc/prgs-health-covid19-analtoolkit.git"
    fig.text(0.01, 0.002, textMsg)
    fig.set_tight_layout(True)
    tFName = sMsg.replace(";","_N_").replace(" ","_")
    fig.savefig("/tmp/{}.svg".format(tFName))
    fig.savefig("/tmp/{}.png".format(tFName))
    plt.show()


def processargs_sel(args, iArg):
    """ Extract the selector set consisting of the dataset name
        and associated geoIds.
        --sel <dataset_name> <geoId1> <geoId2> ...
        """
    numArgs = len(args)
    key = args[iArg]
    iArg += 1
    ids = []
    while iArg < numArgs:
        if args[iArg].startswith("--"):
            break
        ids.append(args[iArg])
        iArg += 1
    return iArg, key, ids


def processargs_and_load(args):
    iArg = 1
    dsAll = []
    selAll = {}
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
        elif args[iArg] == "--sel":
            iArg += 1
            iArg, key, ids = processargs_sel(args, iArg)
            selAll[key] = ids
        else:
            print("ERRR:Main:load_fromargs:UnknownArg:%s"%(args[iArg]))
            iArg += 1
    return dsAll, selAll



if len(sys.argv) <= 1:
    allDS = fetch()
    allSel = {}
else:
    allDS, allSel = processargs_and_load(sys.argv)

ap = analplot.AnalPlot()
#plot_simple(allDS)
plot_sel(allDS, allSel)

# vim: set softtabstop=4 expandtab shiftwidth=4: #
