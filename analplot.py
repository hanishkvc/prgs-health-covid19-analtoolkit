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


    def new_dataset(self):
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


    def _get_data(self, dataKey="raw"):
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
        d, dCH, dRH = self.get_data(dataKey)
        #d = self.data[dataKey]
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


    def calc_scale(self, inDataKey="raw", outDataKey="scale", inMin=None, inMax=None, outMin=0, outMax=1):
        """ Scale the data from inMin-inMax to outMin-outMax
            for each column in the specified input data
            inDataKey: use data saved in this key
            outDataKey: saved result in/using this key
            inMin: Use this as the min value for respective input data cols
                None: Get min from the data cols itself
                a int value: Use this as the min for each data col
                a 1d-array: Use this as the min for each data col
            inMax: Use this as the max value for respective input data cols
            outMin: Use this as the min value for respective output data cols
            outMax: Use this as the max value for respective output data cols
            """
        d, dCH, dRH = self.get_data(inDataKey)
        if inMin == None:
            inMin = np.min(d, axis=0)
        elif type(inMin) == type(int()):
            inMin = np.ones(d.shape[1])*inMin
        if inMax == None:
            inMax = np.max(d, axis=0)
        elif type(inMax) == type(int()):
            inMax = np.ones(d.shape[1])*inMax
        if outMin == None:
            outMin = 0
        if type(outMin) == type(int()):
            outMin = np.ones(d.shape[1])*outMin
        if outMax == None:
            outMax = 1
        if type(outMax) == type(int()):
            outMax = np.ones(d.shape[1])*outMax
        inRange = inMax-inMin
        outRange = outMax-outMin
        newDKey, newCHKey, newRHKey = self._get_datakeys("%s.%s"%(inDataKey, outDataKey))
        self.data[newDKey] = (((d-inMin)/inRange)*outRange)+outMin
        self.data[newRHKey] = dRH
        self.data[newCHKey] = dCH


    def calc_diff(self, dataKey="raw"):
        d, dCH, dRH = self.get_data(dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys("%s.diff"%(dataKey))
        self.data[newDKey] = np.diff(d, axis=0)
        self.data[newRHKey] = dRH[1:]
        self.data[newCHKey] = dCH


    def calc_cumsum(self, dataKey="raw"):
        d, dCH, dRH = self.get_data(dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys("%s.cumsum"%(dataKey))
        self.data[newDKey] = np.cumsum(d, axis=0)
        self.data[newRHKey] = dRH
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


    def calc_movavg_ex(self, dataKey="raw", avgOver=7, times=2, bRoundToDeci8=True):
        d, dCH, dRH = self.get_data(dataKey)
        tWeight = np.ones(avgOver)/avgOver
        dCur = d
        for time in range(times):
            dataConv = np.zeros((dCur.shape[0]-(avgOver-1),dCur.shape[1]))
            for i in range(1,dCur.shape[1]):
                dataConv[:,i] = np.convolve(dCur[:,i], tWeight, 'valid')
            dCur = dataConv
        if bRoundToDeci8:
            dCur = np.round(dCur, 8)
        newDKey, newCHKey, newRHKey = self._get_datakeys("%s.movavgT%d"%(dataKey,times))
        self.data[newDKey] = dCur
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
        d, dCH, dRH = self.get_data(dataKey)
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


    dCalcSimpleFuncs = {
        "diff": calc_diff,
        "cumsum": calc_cumsum,
        "rel2mean": calc_rel2mean,
        "rel2sum": calc_rel2sum,
        "movavg": calc_movavg
    }
    dCalcFuncsWithArg = {
        "movavgT": calc_movavg_ex,
    }
    def get_data(self, dataKey="raw"):
        """ Return the specified data and its col and row headers
            Create them by calling required calc functions, if possible.

            TODO: Need to handle movavgT so as to extract times from name
            """
        if dataKey in self.data:
            return self._get_data(dataKey)
        # This means data not in dict, lets see if we can create it
        [sBDKey, sCmd] = dataKey.rsplit('.',1)
        # Create using a simple calc func
        if sCmd in self.dCalcSimpleFuncs:
            self.dCalcSimpleFuncs[sCmd](self, sBDKey)
            return self._get_data(dataKey)
        for fname in self.dCalcFuncsWithArg:
            if sCmd.startswith(fname):
                if fname == "movavgT":
                    argTimes = int(sCmd.replace("movavgT",""))
                    self.dCalcFuncsWithArg[fname](self, sBDKey, times=argTimes)
                    return self._get_data(dataKey)
        raise NotImplementedError("AnalPlot:get_data:Func[{}] not found...")


    def plot(self, ax, dataKey, plotSelCols=None, title=None, plotLegend=None, plotXTickGap=None, numXTicks=None, xtickMultOf=1, yscale=None, bTranslucent=False):
        tD, tDCH, dRH = self.get_data_selective(dataKey, plotSelCols)
        dprint("DBUG:AnalPlot:plot:\n\tdataKey:%s\n\tFields|ColHdr:%s" %(dataKey, tDCH))
        ax.plot(tD)
        if title != None:
            if title.find("__AUTO__") != -1:
                title = title.replace("__AUTO__", dataKey)
            ax.set_title(title)
        if plotLegend != None:
            ax.legend(tDCH)
        if (numXTicks != None):
            if plotXTickGap != None:
                print("WARN:analplot.plot: numXTicks overrides plotXTickGap")
            plotXTickGap = int(((tD.shape[0]/numXTicks)/xtickMultOf)+1)*xtickMultOf
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
            ax.title.set_alpha(0.4)
            for t in ax.texts:
                t.set_alpha(0.4)


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


    def __newxy_randxy(self, tX, tY):
        tX += np.random.uniform(-tX, tX)*0.01
        tY += np.random.uniform(-tY, tY)*0.01
        return tX, tY


    def __newxy_rotate(self, ax, tX, tY, mode=None):
        if mode == None:
            mode = "rand"
        if mode == "rand":
            r = np.random.randint(8)
        elif mode == "seq":
            try:
                self.newxyRot += 1
            except AttributeError:
                self.newxyRot = 3
            r = self.newxyRot % 8
        xMin, xMax, yMin, yMax = ax.axis()
        xRange = xMax-xMin
        yRange = yMax-yMin
        ratioX = 0.01
        ratioY = ((yRange/xRange)*ratioX)
        print("xRange:%f, yRange:%f; ratioX: %f, ratioY: %f"%(xRange, yRange, ratioX, ratioY))
        if r == 0:
            tX += tX*ratioX
        elif r == 1:
            tY += tY*ratioY
        elif r == 2:
            tX -= tX*ratioX
        elif r == 3:
            tY -= tY*ratioY
        elif r == 4:
            tX += tX*ratioX
            tY += tY*ratioY
        elif r == 5:
            tX += tX*ratioX
            tY -= tY*ratioY
        elif r == 6:
            tX -= tX*ratioX
            tY += tY*ratioY
        elif r == 7:
            tX -= tX*ratioX
            tY -= tY*ratioY
        tY += 0.05*np.log10(yRange)
        return tX, tY


    def _textxy(self, ax, curLoc, curX, curY, curTxt, dX, dY, xscale, yscale):
        if xscale == "log":
            theX = np.log10(dX)
            tX = np.log10(curX)
        else:
            theX = dX
            tX = curX
        if yscale == "log":
            theY = np.log10(dY)
            tY = np.log10(curY)
        else:
            theY = dY
            tY = curY
        xDiff = theX-tX
        yDiff = theY-tY
        xConflict = np.argwhere( (xDiff > -0.02*theX) & (xDiff < 0.02*theX) )
        yConflict = np.argwhere( (yDiff > -0.02*theY) & (yDiff < 0.02*theY) )
        dprint("dX:{}\ndY:{}\nxDiff:{}\nyDiff:{}\nxConflict:{}\nyConflict:{}".format(theX,theY,xDiff,yDiff,xConflict,yConflict))
        tList = []
        for xC in xConflict:
            tC = np.argwhere(yConflict == xC)
            dprint("xC:{}, tC:{}".format(xC, tC))
            if (len(tC) > 0):
                tList.append(xC[0])
        tList = np.array(tList)
        tList = tList[(tList != curLoc)]
        if (len(tList) > 0):
            dprint("dX:{}\ndY:{}\nxDiff:{}\nyDiff:{}\nxConflict:{}\nyConflict:{}".format(theX,theY,xDiff,yDiff,xConflict,yConflict))
            print(curTxt, tX, tY, tList, end="")
            tX, tY = self.__newxy_rotate(ax, tX, tY, "seq")
            print("\tNew: ", tX, tY)
            if xscale == "log":
                curX = 10**tX
            else:
                curX = tX
            if yscale == "log":
                curY = 10**tY
            else:
                curY = tY
        return curX, curY


    def _textxy_super(self, ax, curLoc, curX, curY, curTxt, dX, dY, xscale, yscale):
        pass


    def plotxy(self, ax, dataKeyX, dataKeyY, selRow=-1, plotSelCols=None, title="__AUTO__", xscale="linear", yscale="linear", plotLegend=None, bTranslucent=False):
        """ Plot the specified subset of cols from two related datasets such that
            values of these cols in one of the dataset acts as the x value
            and the values of these cols in the other dataset acts as the y value
            ax: the axes or inset in which to plot.
            dataKeyX: the dataset to use for X axis related values.
            dataKeyY: the dataset to use for Y axis related values.
            selRow: Specifies which row in the given datasets should represent
                the cols in the xy plot.
            plotSelCols: list of cols which should be represented in the plot.
            title: None or title to plot. Specified title can contain "__AUTO__"
                __AUTO__ in title replaced by string "<dataKeyX> vs <dataKeyY>"
            """
        dX, dCHX, dRHX = self.get_data_selective(dataKeyX, plotSelCols)
        dY, dCHY, dRHY = self.get_data_selective(dataKeyY, plotSelCols)
        ax.plot(dX[selRow,:], dY[selRow,:], ".")
        if plotLegend != None:
            textDX = dX[selRow,:]
            textDY = dY[selRow,:]
            for i in range(len(dCHX)):
                tX = dX[selRow,i]
                tY = dY[selRow,i]
                tTxt = dCHX[i]
                tNX, tNY = self._textxy(ax, i, tX, tY, tTxt, textDX, textDY, xscale, yscale)
                textDX[i] = tNX
                textDY[i] = tNY
                ax.arrow(tX,tY, (tNX-tX), (tNY-tY))
                ax.text(tNX, tNY, tTxt)
        if title != None:
            if title.find("__AUTO__") != -1:
                sAuto = "%s vs %s"%(dataKeyX, dataKeyY)
                title = title.replace("__AUTO__", sAuto)
            ax.set_title(title)
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        if bTranslucent:
            ax.set_facecolor([1,1,1,0.1])
            for l in ax.lines:
                l.set_alpha(0.4)
            ax.tick_params(color=[0,0,0,0.4], labelcolor=[0,0,0,0.4])
            ax.title.set_alpha(0.4)
            for t in ax.texts:
                t.set_alpha(0.4)


    def subplots(self, plt, pltRows, pltCols, rowHeight=6, colWidth=9):
        """ Same as pyplot's subplots, except that this also sets the size
            of the figure, based on how many rows and cols are there.
            pltRows: specifies the number of rows in the figure generated
            pltCols: specifies the number of cols in the figure generated
            rowHeight: specifies the size to be alloted per row
            colWidth: specifies the size to be alloted per col
            """
        fig, axes = plt.subplots(pltRows, pltCols)
        figWidth = pltCols*colWidth
        fig.set_figwidth(figWidth)
        figHeight = pltRows*rowHeight
        fig.set_figheight(figHeight)
        xD = 0.8/figWidth
        yD = 0.8/figHeight
        fig.subplots_adjust(xD, yD, 1-xD, 1-yD, 3*xD, 6*yD)
        return fig, axes



def test_textxy():
    d=np.array([[1,10, 200], [40,41,42], [50,41,52],[60,61,62],[40,41,42]])
    ap=AnalPlot()
    ap._textxy(1, 41, 42, "test", d[:,1], d[:,2], "lin", "lin")
    return d



# vim: set softtabstop=4 shiftwidth=4 expandtab: #
