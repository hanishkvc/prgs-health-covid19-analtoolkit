#!/usr/bin/env python3
# Analyse Plot data sets
# v20200430IST1743, HanishKVC
#

import numpy as np
from helpers import *



class AnalPlot:


    def _get_datakeys(self, dataKey="raw"):
        """ get the datakeys required to access a given data
            and its associated column and row headers
            dataKey: the base name used to access/refer to the
                     data and its col header and row header
                     in AnalPlot instance's data dictionary.
            """
        sDKey = dataKey
        sCHKey = "%sColHdr"%(dataKey)
        sRHKey = "%sRowHdr"%(dataKey)
        return sDKey, sCHKey, sRHKey


    def new_dataset():
        """ Setup the current AnalPlot instance to work with
            a new set of data. THis automatically clears any
            prev data that may be stored by this instance.
            """
        self.data = {}


    def set_raw(self, data, rowHdr=None, colHdr=None, dataKey="raw", skipRowsTop=0, skipRowsBottom=-1, skipColsLeft=0, skipColsRight=-1):
        """ Store new raw data along with given row header and col header
            data: the new raw data to store
            colHdr: the associated column | field header
                    i.e what each col corresponds to
            rowHdr: the associated row header
                    i.e what each row corresponds to
            dataKey: the base key to use for refering to this data
            """
        sDKey, sCHKey, sRHKey = self._get_datakeys(dataKey)
        self.data[sDKey] = data
        self.data[sRHKey] = rowHdr
        if type(colHdr) == type(list()):
            colHdr = np.array(colHdr)
        self.data[sCHKey] = colHdr


    def get_data(self, dataKey="raw"):
        """ Return the specified data and its col and row headers
            """
        sDKey, sCHKey, sRHKey = self._get_datakeys(dataKey)
        d = self.data[sDKey]
        dCH = self.data[sCHKey]
        dRH = self.data[sRHKey]
        return d, dCH, dRH


    def get_data_selective(self, dataKey="raw", selCols=None):
        """ Return the specified data and its col and row headers
            ie similar to get_data, except that the returned cols
            correspond to (i.e limited to) specified cols only.
            selCols: gives a list which contains True or False
                corresponding to each col in the dataset.
                Cols with True corresponding to their position,
                will be selected to be returned.
            """
        d, dCH, dRH = self.get_data(dataKey)
        if type(selCols) == type(None):
            tD = d
            tDCH = dCH
        else:
            tD = d[:,selCols]
            tDCH = dCH[selCols]
        return tD, tDCH, dRH


    def get_cols_withval(self, dataKey="raw", val = 0):
        """ Find cols which contain the given val in all its rows
            """
        #d, dCH, dRH = self.get_data(dataKey)
        d = self.data[dataKey]
        colsWithVal = []
        for i in range(d.shape[1]):
            tMin = np.min(d[:,i])
            tMax = np.max(d[:,i])
            if (tMin == val) and (tMax == val):
                colsWithVal.append(i)
        return colsWithVal


    def calc_rel2mean(self, dataKey="raw", bHandleColsWith0=True):
        """ Calculate the mean for each col and store val/mean
            for each val in the respective columns.
            """
        d, dCH, dRH = self.get_data(dataKey)
        if bHandleColsWith0:
            colsWith0 = self.get_cols_withval(dataKey, 0)
        newDKey, newCHKey, newRHKey = self._get_datakeys("%s.rel2mean"%(dataKey))
        self.data[newDKey] = d/np.mean(d, axis=0)
        if bHandleColsWith0:
            self.data[newDKey][:,colsWith0] = 0
        self.data[newRHKey] = dRH
        self.data[newCHKey] = dCH


    def calc_rel2sum(self, dataKey="raw", bHandleColsWith0=True):
        """ Calculate the sum for each col and store value/sum
            for each value in the respective columns.
            """
        d, dCH, dRH = self.get_data(dataKey)
        if bHandleColsWith0:
            colsWith0 = self.get_cols_withval(dataKey, 0)
        newDKey, newCHKey, newRHKey = self._get_datakeys("%s.rel2sum"%(dataKey))
        self.data[newDKey] = d/np.sum(d, axis=0)
        if bHandleColsWith0:
            self.data[newDKey][:,colsWith0] = 0
        self.data[newRHKey] = dRH
        self.data[newCHKey] = dCH


    def calc_diff(self, dataKey="raw"):
        d, dCH, dRH = self.get_data(dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys("%s.diff"%(dataKey))
        self.data[newDKey] = np.diff(d, axis=0)
        self.data[newRHKey] = dRH[1:]
        self.data[newCHKey] = dCH


    def calc_movavg(self, dataKey="raw", avgOver=7):
        d, dCH, dRH = self.get_data(dataKey)
        tWeight = np.ones(avgOver)/avgOver
        dataConv = np.zeros((d.shape[0]-(avgOver-1),d.shape[1]))
        for i in range(1,d.shape[1]):
            dataConv[:,i] = np.convolve(d[:,i], tWeight, 'valid')
        newDKey, newCHKey, newRHKey = self._get_datakeys("%s.movavg"%(dataKey))
        self.data[newDKey] = dataConv
        self.data[newRHKey] = list(range(dataConv.shape[0]))
        self.data[newCHKey] = dCH


    def calc_movavg_ex(self, dataKey="raw", avgOver=7, times=2):
        d, dCH, dRH = self.get_data(dataKey)
        tWeight = np.ones(avgOver)/avgOver
        dCur = d
        for time in range(times):
            dataConv = np.zeros((dCur.shape[0]-(avgOver-1),dCur.shape[1]))
            for i in range(1,dCur.shape[1]):
                dataConv[:,i] = np.convolve(dCur[:,i], tWeight, 'valid')
            dCur = dataConv
        newDKey, newCHKey, newRHKey = self._get_datakeys("%s.movavgT%d"%(dataKey,times))
        self.data[newDKey] = dataConv
        self.data[newRHKey] = list(range(dataConv.shape[0]))
        self.data[newCHKey] = dCH


    def selcols_percentiles(self, dataKey="raw", selRow=-1, selPers=[0,100], bSelInclusive=True, topN=None, botN=None):
        """ Select a set of cols belonging to the specified dataKey, which are within
            the specified percentile range wrt their values in the specified row.
            dataKey: specifies the data set to work with
            selRow: specifies which row in the dataset one should use to calculate
                the percentiles, which will represent the columns.
            selPers: the range of percentiles within which the column should fall
                for it to be selected.
                One could either explicitly specify this or else specify one of
                topN or botN.
            bSelInclusive: Specifies whether the boundry specfied by selPers is
                included in the range of percentiles, when selecting the cols.
            topN: If specified, this is used to decide the selPers to be used.
                If one requires to select the top N columns in the dataset, based
                on the percentile calculation for the given row in the dataset,
                use this.
            botN: If specified, this is used to decide the selPers to be used.
                If one requires to select the bottom N columns in the dataset,
                based on percentile calculation for given row in the dataset,
                use this.
            """
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
        tD, tDCH, dRH = self.get_data_selective(dataKey, plotSelCols)
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
        tD, tDCH, dRH = self.get_data_selective(dataKey, plotSelCols)
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


    def plotxy(self, ax, dataKeyX, dataKeyY, selRow=-1, plotSelCols=None, title=None):
        """ Plot the specified subset of cols from two related datasets such that
            values of these cols in one of the dataset acts as the x value
            and the values of these cols in the other dataset acts as the y value
            ax: the axes or inset in which to plot.
            dataKeyX: the dataset to use for X axis related values.
            dataKeyY: the dataset to use for Y axis related values.
            selRow: Specifies which row in the given datasets should represent
                the cols in the xy plot.
            plotSelCols: list of cols which should be represented in the plot.
            """
        dX, dCHX, dRHX = self.get_data_selective(dataKeyX, plotSelCols)
        dY, dCHY, dRHY = self.get_data_selective(dataKeyY, plotSelCols)
        ax.plot(dX[selRow,:], dY[selRow,:])
        if title != None:
            ax.set_title(title)


    def subplots(self, plt, pltRows, pltCols, rowHeight=6, colWidth=9):
        """ Same as pyplot's subplots, except that this also sets the size
            of the figure, based on how many rows and cols are there.
            pltRows: specifies the number of rows in the figure generated
            pltCols: specifies the number of cols in the figure generated
            rowHeight: specifies the size to be alloted per row
            colWidth: specifies the size to be alloted per col
            """
        fig, axes = plt.subplots(pltRows, pltCols)
        fig.set_figwidth(pltCols*colWidth)
        fig.set_figheight(pltRows*rowHeight)
        return fig, axes


# vim: set softtabstop=4 shiftwidth=4 expandtab: #
