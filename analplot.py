#!/usr/bin/env python3
# Analyse Plot data sets
# v20200430IST1743, HanishKVC
# 

import numpy as np
from helpers import *



class AnalPlot:


    def set_raw(self, data, rowHdr=None, colHdr=None, skipRowsTop=0, skipRowsBottom=-1, skipColsLeft=0, skipColsRight=-1):
        self.data = {}
        self.data["raw"] = data
        self.data["rawRowHdr"] = rowHdr
        if type(colHdr) == type(list()):
            colHdr = np.array(colHdr)
        self.data["rawColHdr"] = colHdr


    def calc_rel2mean(self, dataSel="raw"):
        d = self.data[dataSel]
        dCH = self.data["{}ColHdr".format(dataSel)]
        dRH = self.data["{}RowHdr".format(dataSel)]
        self.data["{}.rel2mean".format(dataSel)] = d/np.mean(d, axis=0)
        self.data["{}.rel2meanRowHdr".format(dataSel)] = dRH
        self.data["{}.rel2meanColHdr".format(dataSel)] = dCH


    def calc_rel2sum(self, dataSel="raw"):
        d = self.data[dataSel]
        dCH = self.data["{}ColHdr".format(dataSel)]
        dRH = self.data["{}RowHdr".format(dataSel)]
        self.data["{}.rel2sum".format(dataSel)] = d/np.sum(d, axis=0)
        self.data["{}.rel2sumRowHdr".format(dataSel)] = dRH
        self.data["{}.rel2sumColHdr".format(dataSel)] = dCH


    def calc_movavg(self, dataSel="raw", avgOver=7):
        d = self.data[dataSel]
        dCH = self.data["{}ColHdr".format(dataSel)]
        dRH = self.data["{}RowHdr".format(dataSel)]
        tWeight = np.ones(avgOver)/avgOver
        dataConv = np.zeros((d.shape[0]-(avgOver-1),d.shape[1]))
        for i in range(1,d.shape[1]):
            dataConv[:,i] = np.convolve(d[:,i], tWeight, 'valid')
        self.data["{}.movavg".format(dataSel)] = dataConv
        self.data["{}.movavgRowHdr".format(dataSel)] = list(range(dataConv.shape[0]))
        self.data["{}.movavgColHdr".format(dataSel)] = dCH


    def selcols_percentiles(self, dataSel="raw", selRow=-1, selPers=[0,100], bSelInclusive=True, topN=None, botN=None):
        d = self.data[dataSel]
        if (topN != None) and (botN != None):
            print("WARN:AnalPlot:selcols_percentile: botN takes priority if both topN & botN specified")
        if topN != None:
            iPercentile = (topN/d.shape[1])*100
            selPers = [(100-iPercentile), 100]
        if botN != None:
            iPercentile = (botN/d.shape[1])*100
            selPers = [0, iPercentile]
        if (topN != None) or (botN != None):
            print("INFO:AnalPlot:selcols_percentile:range:{}".format(selPers))
        #thePercentiles = np.percentile(d[selRow:,:], selPers, axis=1)
        thePercentiles = np.percentile(d[selRow,:], selPers)
        if bSelInclusive:
            selCols = (d[selRow,:] >= thePercentiles[0]) & (d[selRow,:] <= thePercentiles[1])
        else:
            selCols = (d[selRow,:] > thePercentiles[0]) & (d[selRow,:] < thePercentiles[1])
        return selCols, selPers


    def plot(self, ax, dataSel, plotSelCols=None, plotLegend=None, plotXTickGap=None, numXTicks=None, xtickMultOf=1, yscale=None):
        d = self.data[dataSel]
        dCH = self.data["{}ColHdr".format(dataSel)]
        dRH = self.data["{}RowHdr".format(dataSel)]
        if type(plotSelCols) == type(None):
            tD = d
            tDCH = dCH
        else:
            tD = d[:,plotSelCols]
            tDCH = dCH[plotSelCols]
        dprint("DBUG:AnalPlot:plot:hdr-type:%s" %(type(tDCH[5])))
        ax.plot(tD)
        if plotLegend != None:
            ax.legend(tDCH)
        if (numXTicks != None):
            if plotXTickGap != None:
                print("WARN:analplot.plot: numXTicks overrides plotXTickGap")
            plotXTickGap = int(((d.shape[0]/numXTicks)/xtickMultOf)+1)*xtickMultOf
        if plotXTickGap != None:
            ax.set_xticks(np.arange(0, dRH.shape[0], plotXTickGap))
            ax.set_xticklabels(dRH[0::plotXTickGap])
        if yscale != None:
            ax.set_yscale(yscale)


    def boxplot(self, ax, dataSel, plotSelCols=None, title=None, bInsetBoxPlot=False):
        d = self.data[dataSel]
        dCH = self.data["{}ColHdr".format(dataSel)]
        dRH = self.data["{}RowHdr".format(dataSel)]
        if type(plotSelCols) == type(None):
            tD = d
            tDCH = dCH
        else:
            tD = d[:,plotSelCols]
            tDCH = dCH[plotSelCols]
        ax.boxplot(tD,labels=tDCH)
        if title != None:
            ax.set_title(title)
        if bInsetBoxPlot:
            inset = ax.inset_axes([0.0,0.5,1.0,0.5])
            inset.boxplot(tD,labels=tDCH)
            inset.set_yscale("log")
            for l in inset.lines:
                l.set_alpha(0.2)
            #inset.set_alpha(0.5)
            inset.set_facecolor([1,1,1,0.1])
            inset.tick_params(color=[1,0,0,0.2], labelcolor=[1,0,0,0.2])
            inset.grid(True, axis='y')


    def subplots(self, plt, pltRows, pltCols, rowHeight=6, colWidth=9):
        fig, axes = plt.subplots(pltRows, pltCols)
        fig.set_figwidth(pltCols*colWidth)
        fig.set_figheight(pltRows*rowHeight)
        return fig, axes


# vim: set softtabstop=4 shiftwidth=4 expandtab: #
