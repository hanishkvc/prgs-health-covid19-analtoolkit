#!/usr/bin/env python3
# Analyse Plot data sets
# v20200430IST1743, HanishKVC
# 

import numpy as np
from helpers import *



class AnalPlot:


    def _get_datakeys(self, dataKey="raw"):
        sDKey = dataKey
        sCHKey = "%sColHdr"%(dataKey)
        sRHKey = "%sRowHdr"%(dataKey)
        return sDKey, sCHKey, sRHKey


    def set_raw(self, data, rowHdr=None, colHdr=None, dataKey="raw", skipRowsTop=0, skipRowsBottom=-1, skipColsLeft=0, skipColsRight=-1):
        self.data = {}
        sDKey, sCHKey, sRHKey = self._get_datakeys(dataKey)
        self.data[sDKey] = data
        self.data[sRHKey] = rowHdr
        if type(colHdr) == type(list()):
            colHdr = np.array(colHdr)
        self.data[sCHKey] = colHdr


    def get_basedata(self, dataKey="raw"):
        d = self.data[dataKey]
        dCH = self.data["{}ColHdr".format(dataKey)]
        dRH = self.data["{}RowHdr".format(dataKey)]
        return d, dCH, dRH


    def get_cols_withval(self, dataKey="raw", val = 0):
        """ Find cols which contain the given val in all its rows
            """
        #d, dCH, dRH = self.get_basedata(dataKey)
        d = self.data[dataKey]
        colsWithVal = []
        for i in range(d.shape[1]):
            tMin = np.min(d[:,i])
            tMax = np.max(d[:,i])
            if (tMin == val) and (tMax == val):
                colsWithVal.append(i)
        return colsWithVal


    def calc_rel2mean(self, dataKey="raw", bHandleColsWith0=True):
        d, dCH, dRH = self.get_basedata(dataKey)
        if bHandleColsWith0:
            colsWith0 = self.get_cols_withval(dataKey, 0)
        self.data["{}.rel2mean".format(dataKey)] = d/np.mean(d, axis=0)
        if bHandleColsWith0:
            self.data["{}.rel2mean".format(dataKey)][:,colsWith0] = 0
        self.data["{}.rel2meanRowHdr".format(dataKey)] = dRH
        self.data["{}.rel2meanColHdr".format(dataKey)] = dCH


    def calc_rel2sum(self, dataKey="raw", bHandleColsWith0=True):
        d, dCH, dRH = self.get_basedata(dataKey)
        if bHandleColsWith0:
            colsWith0 = self.get_cols_withval(dataKey, 0)
        self.data["{}.rel2sum".format(dataKey)] = d/np.sum(d, axis=0)
        if bHandleColsWith0:
            self.data["{}.rel2sum".format(dataKey)][:,colsWith0] = 0
        self.data["{}.rel2sumRowHdr".format(dataKey)] = dRH
        self.data["{}.rel2sumColHdr".format(dataKey)] = dCH


    def calc_diff(self, dataKey="raw"):
        d, dCH, dRH = self.get_basedata(dataKey)
        self.data["{}.diff".format(dataKey)] = np.diff(d, axis=0)
        self.data["{}.diffRowHdr".format(dataKey)] = dRH[1:]
        self.data["{}.diffColHdr".format(dataKey)] = dCH


    def calc_movavg(self, dataKey="raw", avgOver=7):
        d, dCH, dRH = self.get_basedata(dataKey)
        tWeight = np.ones(avgOver)/avgOver
        dataConv = np.zeros((d.shape[0]-(avgOver-1),d.shape[1]))
        for i in range(1,d.shape[1]):
            dataConv[:,i] = np.convolve(d[:,i], tWeight, 'valid')
        self.data["{}.movavg".format(dataKey)] = dataConv
        self.data["{}.movavgRowHdr".format(dataKey)] = list(range(dataConv.shape[0]))
        self.data["{}.movavgColHdr".format(dataKey)] = dCH


    def calc_movavg_ex(self, dataKey="raw", avgOver=7, times=2):
        d, dCH, dRH = self.get_basedata(dataKey)
        tWeight = np.ones(avgOver)/avgOver
        dCur = d
        for time in range(times):
            dataConv = np.zeros((dCur.shape[0]-(avgOver-1),dCur.shape[1]))
            for i in range(1,dCur.shape[1]):
                dataConv[:,i] = np.convolve(dCur[:,i], tWeight, 'valid')
            dCur = dataConv
        self.data["{}.movavgT{}".format(dataKey,times)] = dataConv
        self.data["{}.movavgT{}RowHdr".format(dataKey,times)] = list(range(dataConv.shape[0]))
        self.data["{}.movavgT{}ColHdr".format(dataKey,times)] = dCH


    def selcols_percentiles(self, dataKey="raw", selRow=-1, selPers=[0,100], bSelInclusive=True, topN=None, botN=None):
        d = self.data[dataKey]
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


    def plot(self, ax, dataKey, plotSelCols=None, title=None, plotLegend=None, plotXTickGap=None, numXTicks=None, xtickMultOf=1, yscale=None, bTranslucent=False):
        d, dCH, dRH = self.get_basedata(dataKey)
        if type(plotSelCols) == type(None):
            tD = d
            tDCH = dCH
        else:
            tD = d[:,plotSelCols]
            tDCH = dCH[plotSelCols]
        dprint("DBUG:AnalPlot:plot:\n\tdataKey:%s\n\tFields|ColHdr:%s" %(dataKey, tDCH))
        ax.plot(tD)
        if title != None:
            ax.set_title(title)
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
        if bTranslucent:
            ax.set_facecolor([1,1,1,0.1])
            for l in ax.lines:
                l.set_alpha(0.4)
            ax.tick_params(color=[0,0,0,0.4], labelcolor=[0,0,0,0.4])


    def boxplot(self, ax, dataKey, plotSelCols=None, title=None, bInsetBoxPlot=False):
        d, dCH, dRH = self.get_basedata(dataKey)
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
            inset.tick_params(color=[1,0,0,0.4], labelcolor=[1,0,0,0.4])
            inset.grid(True, axis='y')


    def subplots(self, plt, pltRows, pltCols, rowHeight=6, colWidth=9):
        fig, axes = plt.subplots(pltRows, pltCols)
        fig.set_figwidth(pltCols*colWidth)
        fig.set_figheight(pltRows*rowHeight)
        return fig, axes


# vim: set softtabstop=4 shiftwidth=4 expandtab: #
