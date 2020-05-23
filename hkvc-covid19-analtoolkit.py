#!/usr/bin/env python3
# Covid19 AnalToolkit
# v20200520IST2217, HanishKVC
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
        ap.plot(axes[1,iCur], "cases/day>rel2mean", title="%s-Cases/Day_Rel2Mean"%(ds.name))
        ap.calc_rel2sum("cases/day")
        ap.plot(axes[2,iCur], "cases/day>rel2sum", title="%s-Cases/Day_Rel2Sum"%(ds.name))
        ap.calc_movavg("cases/day")
        selCols, selPers = ap.selcols_percentiles("cases/day>movavg")
        ap.plot(axes[3,iCur], "cases/day>movavg", plotSelCols=selCols, title="%s-Cases/Day_MovAvg"%(ds.name))
        sGlobalMsg += "{}-Data-{}_{}--".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCur += 1
    save_fig(fig, sGlobalMsg)


def sel_cols(dataKey, topN, inSelIds, baseTitle, selTitle, bSelInclusive=True):
    if inSelIds == None:
        selCols, selPers = ap.selcols_percentiles(dataKey, topN=topN, bSelInclusive=bSelInclusive)
        theTitle = "%s-%sTop%d"%(baseTitle, selTitle, topN)
    else:
        selCols = ap.selcols_colhdr(dataKey, inSelIds)
        theTitle = baseTitle+"-user%d"%(len(inSelIds))
    return selCols, theTitle


# When plotting scaled Diff data on a log scale, the entry
# which corresponds to 0 in x or y axis will not be shown,
# because plotxy will keep 0 out of its plot window using its
# axis_adjust logic.
bMODE_SCALEDIFF=True
def plot_xy(ds, ap, axes, iARow, iACol, dataKey, topNCS, topND, inSelIds):
    """ PlotXY data based on cumsum and diff.movavg topN
        """
    selCols, theTitle = sel_cols("%s>cumsum"%(dataKey), topNCS, inSelIds, "%s-__AUTO__"%(ds.name),"cumsum", bSelInclusive=True)
    if False:
        colorControlVals = np.ones(ap.data[dataKey].shape[1])
        colorControlVals[0:int(len(colorControlVals)/2)] = -1
    else:
        theGSCols, colorControlVals = ap.group_simple(dataKey, selCols, dataOps="diff>movavg(T=2)")
        print("DBUG:Main:plot_xy:selCols:{}; GroupSimpleCols:{}".format(selCols, theGSCols))
    ap.plotxy(axes[iARow,iACol], "%s>cumsum"%(dataKey), "%s>movavg"%(dataKey), plotSelCols=selCols,
                title=theTitle, xscale="log", yscale="log", plotLegend=True, colorControlVals=colorControlVals, colorMarkers=['g.','r.'])
    inset = axes[iARow,iACol].inset_axes([0.6,0.10,0.4,0.4])
    if bMODE_SCALEDIFF:
        ap.calc_scale("%s>diff>movavg(T=2)"%(dataKey), axis=1)
        yDataKey = "%s>diff>movavg(T=2)>scale"%(dataKey)
        sAddTitle = "scale"
    else:
        yDataKey = "%s>diff>movavg(T=2)"%(dataKey)
        sAddTitle = ""
    selCols, theTitle = sel_cols("%s>diff>movavg(T=2)"%(dataKey), topND, inSelIds, "Cases/Day MAvVsDifMAvT2%s"%(sAddTitle),"DifMAvT2", bSelInclusive=True)
    ap.plotxy(inset, "%s>movavg"%(dataKey), yDataKey, plotSelCols=selCols, bTranslucent=True,
                title=theTitle, xscale="log", yscale="log", plotLegend=True)
    analplot.textxy_spread("default")
    return iARow+1


def plot_data_diffTopN(ds, ap, axes, iARow, iACol, dataKey="cases/day", topN=8, inSelIds=None):
    """ Plot data based on Cases/Day>Diff>MovingAvg TopN
        """
    selCols, theTitle = sel_cols("%s>diff>movavg(T=2)"%(dataKey), topN, inSelIds, "%s-__AUTO__"%(ds.name),"DiffMovAvgT2")
    ap.plot(axes[iARow,iACol], "%s>rel2sum>movavg(T=2)"%(dataKey), plotSelCols=selCols, plotLegend=True,
                title=theTitle)
    inset = axes[iARow,iACol].inset_axes([0.13,0.55,0.64,0.4])
    ap.plot(inset, "%s>diff>movavg(T=3)"%(dataKey), plotSelCols=selCols, plotLegend=None, bTranslucent=True,
                title=theTitle)
    return iARow+1


def plot_data_movavgTopN(ds, ap, axes, iARow, iACol, dataKey="cases/day", topN=8, inSelIds=None):
    """ Plot data of regions selected based on cases/day>movavgTopN
        """
    theTitle = "%s-__AUTO__"%(ds.name)
    selCols, theTitle = sel_cols("%s>movavg"%(dataKey), topN, inSelIds, theTitle, "movavg")
    ap.plot(axes[iARow,iACol], "%s>movavg"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle, yscale="log")
    yscale = None
    inset = axes[iARow,iACol].inset_axes([0.36,0.05,0.64,0.4])
    ap.plot(inset, "%s>rel2sum>movavg(T=2)"%(dataKey), plotSelCols=selCols, yscale=yscale, bTranslucent=True, numXTicks=4, xtickMultOf=7, title=theTitle)
    return iARow+1


def boxplot_data_movavgTopN(ds, ap, axes, iARow, iACol, dataKey="cases/day", topN=20, inSelIds=None):
    """ BoxPlot data of regions selected based on cases/day>movavgTopN
        """
    theTitle = "%s-__AUTO__"%(ds.name)
    selCols, theTitle = sel_cols("%s>movavg"%(dataKey), topN, inSelIds, theTitle, "movavg")
    ap.boxplot(axes[iARow,iACol], dataKey, plotSelCols=selCols, bInsetBoxPlot=True, title=theTitle)
    return iARow+1


def plot_sel(allDS, allSel):
    """ Plot a set of interesting/informative/... plots
        Uses the new auto calc as required functionality of AnalPlot
        """
    fig, axes = ap.subplots(plt,4,len(allDS))
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
        iARow = 0
        # PlotXY data based on cumsum and diff topN
        iARow = plot_xy(ds, ap, axes, iARow, iCurDS, "cases/day", 25, 8, theSelIds)
        # Boxplot Raw data based on Cases/Day>MovingAvg TopN
        iARow = boxplot_data_movavgTopN(ds, ap, axes, iARow, iCurDS, "cases/day", 25, theSelIds)
        # Plot data based on Cases/Day>MovingAvg TopN
        iARow = plot_data_movavgTopN(ds, ap, axes, iARow, iCurDS, "cases/day", 8, theSelIds)
        # Plot data based on Cases/Day>Diff>MovingAvg TopN
        iARow = plot_data_diffTopN(ds, ap, axes, iARow, iCurDS, "cases/day", 8, theSelIds)
        sGlobalMsg += "{}-Data-{}_{}--".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCurDS += 1
    save_fig(fig, sGlobalMsg)


def _plot_movavgs(ap, axes, iRow, iCol, dataKey, selCols, theTitle):
    ap.plot(axes[iRow+0,iCol], dataKey, plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+1,iCol], "%s>movavg"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+2,iCol], "%s>movavg(T=2)"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+3,iCol], "%s>movavg(T=3)"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+4,iCol], "%s>movavg(T=4)"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    return iRow+5


bTEST_MIXMATCH=False
def plot_mixmatch(allDS, allSel):
    """ Plot a set of interesting/informative/... plots
        Uses the new auto calc as required functionality of AnalPlot
        """
    for ds in allDS:
        fig, axes = ap.subplots(plt,5,4)
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
        theTitle = "%s-__AUTO__"%(ds.name)
        selCols, theTitle = sel_cols("cases/day>movavg", topN, theSelIds, theTitle, "movavg")
        _plot_movavgs(ap, axes, 0, 0, "cases/day", selCols, theTitle)
        _plot_movavgs(ap, axes, 0, 1, "cases/day>scale", selCols, theTitle)
        _plot_movavgs(ap, axes, 0, 2, "cases/day>rel2sum", selCols, theTitle)
        _plot_movavgs(ap, axes, 0, 3, "cases/day>diff", selCols, theTitle)
        sGlobalMsg = "MMMA-{}-Data-{}_{}--".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
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
    global bMODE_SCALEDIFF
    global bTEST_MIXMATCH
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
        elif args[iArg] == "--no_scalediff":
            bMODE_SCALEDIFF = False
            iArg += 1
        elif args[iArg] == "--scalediff":
            bMODE_SCALEDIFF = True
            iArg += 1
        elif args[iArg] == "--test_mixmatch":
            bTEST_MIXMATCH = True
            iArg += 1
        else:
            print("ERRR:Main:load_fromargs:UnknownArg:%s"%(args[iArg]))
            iArg += 1
    return dsAll, selAll



allDS, allSel = processargs_and_load(sys.argv)
if len(allDS) == 0:
    allDS = fetch()

ap = analplot.AnalPlot()
#plot_simple(allDS)
plot_sel(allDS, allSel)
if bTEST_MIXMATCH:
    plot_mixmatch(allDS, allSel)

# vim: set softtabstop=4 expandtab shiftwidth=4: #
