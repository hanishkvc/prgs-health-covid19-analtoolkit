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


def ap_setraw(ap, ds, dataKey):
    ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr[2:], dataKey=dataKey)
    if ds.name == "Cov19In":
        lSkip = [ 'UN' ]
        print("WARN:Main:ap_setraw:%s:Skipping region %s"%(ds.name, lSkip))
        selCols = ap.selcols_colhdr(dataKey, lSkip)
        selCols = ~np.array(selCols)
        d, dCH, dRH = ap.get_data_selective(dataKey, selCols)
        ap.del_data(dataKey)
        ap.set_raw(d, dRH, dCH, dataKey)


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
        ap_setraw(ap, ds, "cases/day")
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
sPLOTXY_GSTYPE="gsn"
def plot_xy(ds, ap, axes, iARow, iACol, dataKey, topNCS, topND, inSelIds):
    """ PlotXY data based on cumsum and diff.movavg topN
        It also highlights the regions where cases/day is changing
        in a relatively worse fashion, in red.
        """
    selCols, theTitle = sel_cols("%s>cumsum"%(dataKey), topNCS, inSelIds, "%s-__AUTO__"%(ds.name),"cumsum", bSelInclusive=True)
    if False:
        markerControlVals = np.ones(ap.data[dataKey].shape[1])
        markerControlVals[0:int(len(markerControlVals)/2)] = -1
    else:
        if sPLOTXY_GSTYPE == "gsp":
            theGSCols, markerControlVals = ap.groupsimple_percentiles_ex(dataKey, selCols, dataOps="diff>movavg(T=2)", percentileRanges=[0,30,70,100])
            mCL = [0,1,2]
            markers = ['c.','r.','ro']
        else:
            gsnKey = "%s>rel2sum>movavg(T=2)"%(dataKey)
            theGSCols, lc, markerControlVals = ap.groupsimple_neighbours_ex(gsnKey, gsnKey, selCols=selCols, selRows=None, numOfGroups=6, maxTries=24)
            mCL = list(range(len(lc)))
            markers = ['g.','c.','c*','r.','r*','ro']
        print("DBUG:Main:plot_xy:selCols:{}; GroupSimpleCols:{}".format(selCols, theGSCols))
    ap.plotxy(axes[iARow,iACol], "%s>cumsum"%(dataKey), "%s>movavg"%(dataKey), plotSelCols=selCols,
                title=theTitle, xscale="log", yscale="log", plotLegend=True, markerControlVals=markerControlVals, markerControlLimits=mCL, markers=markers)
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


bPLOTSEL_PARTIAL=False
def plot_sel(allDS, allSel):
    """ Plot a set of interesting/informative/... plots
        Uses the new auto calc as required functionality of AnalPlot
        """
    numRows = 4
    sGMsgSuffix = ""
    if bPLOTSEL_PARTIAL:
        sGMsgSuffix = "part"
        numRows = 2
    fig, axes = ap.subplots(plt,numRows,len(allDS))
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
        ap_setraw(ap, ds, "cases/day")
        iARow = 0
        # PlotXY data based on cumsum and diff topN
        iARow = plot_xy(ds, ap, axes, iARow, iCurDS, "cases/day", 25, 8, theSelIds)
        # Boxplot Raw data based on Cases/Day>MovingAvg TopN
        iARow = boxplot_data_movavgTopN(ds, ap, axes, iARow, iCurDS, "cases/day", 25, theSelIds)
        if not bPLOTSEL_PARTIAL:
            # Plot data based on Cases/Day>MovingAvg TopN
            iARow = plot_data_movavgTopN(ds, ap, axes, iARow, iCurDS, "cases/day", 8, theSelIds)
            # Plot data based on Cases/Day>Diff>MovingAvg TopN
            iARow = plot_data_diffTopN(ds, ap, axes, iARow, iCurDS, "cases/day", 8, theSelIds)
        sGlobalMsg += "{}-Data-{}_{}--".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
        iCurDS += 1
    sGlobalMsg += sGMsgSuffix
    save_fig(fig, sGlobalMsg)


def _plot_movavgs(ap, axes, iRow, iCol, dataKey, selCols, theTitle):
    """ Plot given data after applying
            movavg for different number of times on that data
            movavg with different windowSizes on that data.
        """
    ap.plot(axes[iRow+0,iCol], dataKey, plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+1,iCol], "%s>movavg"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+2,iCol], "%s>movavg(T=2)"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+3,iCol], "%s>movavg(T=3)"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+4,iCol], "%s>movavg(T=4)"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+5,iCol], "%s>movavg(W=14)"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+6,iCol], "%s>movavg(W=21)"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    ap.plot(axes[iRow+7,iCol], "%s>movavg(W=28)"%(dataKey), plotSelCols=selCols, plotLegend=True, title=theTitle)
    return iRow+8


bTEST_MIXMATCH=False
def plot_mixmatch(allDS, allSel):
    """ Plot a set of interesting/informative/... plots
        Uses the new auto calc as required functionality of AnalPlot
        """
    for ds in allDS:
        fig, axes = ap.subplots(plt,9,4)
        ap.new_dataset()
        if ds.name in allSel:
            theSelIds = allSel[ds.name]
        else:
            theSelIds = None
        dprint("DBUG:Main:plot_sel:hdr-type:%s" %(type(ds.hdr[-2])))
        # The Raw data
        ap_setraw(ap, ds, "cases/day")
        # Plot moving avg of raw data and its processed representations
        topN=8
        theTitle = "%s-__AUTO__"%(ds.name)
        selCols, theTitle = sel_cols("cases/day>movavg", topN, theSelIds, theTitle, "movavg")
        colDataKeys = [ "cases/day", "cases/day>scale", "cases/day>rel2sum", "cases/day>diff" ]
        rowDataKeys = [ "", "movavg", "movavg(T=2)", "movavg(T=3)", "movavg(T=4)", "movavg(W=14)", "movavg(W=21)", "movavg(W=28)", "movavg(W=49)" ]
        analplot.plot_matrix(ap, rowDataKeys, colDataKeys, axes, 0, 0, plotSelCols=selCols, title=theTitle, plotLegend=True, axis=0)
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
    global sPLOTXY_GSTYPE
    global bPLOTSEL_PARTIAL
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
        elif args[iArg] == "--plotxy_gsp":
            sPLOTXY_GSTYPE = "gsp"
            iArg += 1
        elif args[iArg] == "--plotxy_gsn":
            sPLOTXY_GSTYPE = "gsn"
            iArg += 1
        elif args[iArg] == "--plotsel_partial":
            bPLOTSEL_PARTIAL = True
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
