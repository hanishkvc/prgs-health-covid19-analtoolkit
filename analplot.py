#!/usr/bin/env python3
# Analyse Plot data sets
# v20200512IST1126, HanishKVC
# LGPL
#

import numpy as np
from helpers import *
import sys



DBG_PLOTXYRECT_MSG=False

DEF_CHARXPIXELS=6
DEF_CHARYPIXELS=9
CHAR_XPIXELS=DEF_CHARXPIXELS
CHAR_YPIXELS=DEF_CHARYPIXELS
CHAR_NONORIENTATION_MULT=1.2
def textxy_spread(mode="default", mult=1):
    """ Use this to make the textxy overlap avoidance be either
        "far": more spread out
        "near": more near to one another
        "default": to set the levers back to default value
        "custom": you specify the multiplier to apply to the levers
        """
    global CHAR_XPIXELS, CHAR_YPIXELS, CHAR_NONORIENTATION_MULT
    if mode == "default":
        CHAR_XPIXELS=DEF_CHARXPIXELS
        CHAR_YPIXELS=DEF_CHARYPIXELS
        CHAR_NONORIENTATION_MULT=1.2
    elif mode == "far":
        CHAR_XPIXELS *= 1.2
        CHAR_YPIXELS *= 1.2
        CHAR_NONORIENTATION_MULT *= 1.2
    elif mode == "near":
        CHAR_XPIXELS *= 0.8
        CHAR_YPIXELS *= 0.8
        CHAR_NONORIENTATION_MULT *= 0.8
    elif mode == "custom":
        CHAR_XPIXELS *= mult
        CHAR_YPIXELS *= mult
        CHAR_NONORIENTATION_MULT *= mult
    else:
        raise NotImplementedError



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


    def _initdbg_axisadjust(self):
        self.dbgAxisAdjustCntr = 1


    def new_dataset(self):
        """ Setup the current AnalPlot instance to work with
            a new set of data. THis automatically clears any
            prev data that may be stored by this instance.
            """
        self.data = {}
        self._initdbg_axisadjust()


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
        """ Plot the specified dataset's data columns or a subset of its columns on the given
                axes (ax).

            dataKey: decides which set of data inside the current analplot instance is used.
            plotSelCols: decides if only a subset of the cols need to be plotted.
            title: None or title to plot. Specified title can contain "__AUTO__"
                __AUTO__ in title replaced by string "<dataKey>"
            plotXTickGap: Specifies what should be the gap between x-axis ticks.
                This is specified interms of how many data points along x-axis to skip
                from tick marking on the plot, which in this case is rows of data.
                The number of ticks will depend on amount of data available along x-axis.
            numXTicks: Or else One can specify the number of ticks required along x-axis
                and let the logic to decide the plotXTickGap required based on the total
                data points available along x-axis, automatically.
                One can even control the plotXTickGap to be a multiple of some number
                in this case by specifying xtickMultOf argument. For example when plotting
                data where x-axis corresponds to days, one can ask the ticks to relate to
                roughly weeks or months or so, by setting xtickMultOf arg to 7 or 30 ...
            bTranslucent: Will make the ticks, labels, title, lines to be translucent.
                This is useful, if this is a inset being plotted on top of another plot.
            plotLegend: list of legends corresponding to each column of data being plotted.
            yscale: If specified y-axis can use log scale instead of the default linear.
            """
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
        iX = tX
        iY = tY
        if mode == None:
            mode = "rand"
        if mode == "rand":
            r = np.random.randint(8)
        elif mode == "seq":
            try:
                self.newxyRot += 1
            except AttributeError:
                self.newxyRot = 0
            r = self.newxyRot % 8
            mult = (int(self.newxyRot/16)/16)+1
        ratioX = 0.01
        ratioY = ((self.textxyYRange/self.textxyXRange)*ratioX)
        ratioX = self.textxyCharPixRatioX
        ratioY = self.textxyCharPixRatioY
        deltaX = ratioX*self.textxyXRange*mult
        deltaY = ratioY*self.textxyYRange*mult
        if r == 0:
            tX += deltaX
        elif r == 1:
            tY += deltaY
        elif r == 2:
            tX -= deltaX
        elif r == 3:
            tY -= deltaY
        elif r == 4:
            tX += deltaX
            tY += deltaY
        elif r == 5:
            tX += deltaX
            tY -= deltaY
        elif r == 6:
            tX -= deltaX
            tY += deltaY
        elif r == 7:
            tX -= deltaX
            tY -= deltaY
        #tY += deltaY*2
        dprint("DBUG:AnalPlot:newxy:xRange:%f, yRange:%f; ratioX: %f, ratioY: %f; deltaX: %f, deltaY: %f; %f,%f=>%f,%f"
                %(self.textxyXRange, self.textxyYRange, ratioX, ratioY, deltaX, deltaY, iX,iY, tX,tY))
        return tX, tY


    def _test_plotxy_rect(self, ax, x1, y1, x2, y2, xscale="linear", yscale="linear", sMsgT=None, sMsgB=None):
        """ Plot the 4 edge vertices of the rectangle specified.
            It assumes that the x and y info passed to it, is in the
            same scale as specified by xscale and yscale. So it takes
            care of converting them into normal value before calling
            the plot logic, bcas the plot logic takes normal values,
            what ever they may be, and then plots them and scales them
            as required/specified by the xscale and yscale passed to it.

            It also allows one to plot 2 messages next to the rectangle,
            one next to the top right edge and one next to the bottom
            right edge of the rectangle.
            """
        lX = [ x1,x1,x2,x2]
        lY = [ y1,y2,y1,y2]
        lX = np.array(lX)
        if xscale == "log":
            lXO = 10**lX
            X2 = 10**x2
        else:
            lXO = lX
            X2 = x2
        lY = np.array(lY)
        if yscale == "log":
            lYO = 10**lY
            Y2 = 10**y2
            Y1 = 10**y1
        else:
            lYO = lY
            Y2 = y2
            Y1 = y1
        print("DBUG:AnalPlot:_TestPlotXYRect: lX {}, lY {}, lXO {}, lYO {}; sMsgT {}, sMsgB {}".format(lX, lY, lXO, lYO, sMsgT, sMsgB))
        ax.plot(lXO,lYO,"xg")
        if (sMsgT != None) and DBG_PLOTXYRECT_MSG:
            ax.text(X2,Y2, sMsgT)
        if (sMsgB != None) and DBG_PLOTXYRECT_MSG:
            ax.text(X2,Y1, sMsgB)


    def test_plotxy_rect(self, ax, idCheck, x1, y1, x2, y2, xscale="linear", yscale="linear", sMsgT=None, sMsgB=None):
        """ Plot the rectangle specified provided it meets the criteria set by
            info in the given dTestPlotXYRect instance variable.

            idCheck is the id to associate with the current rect plot request.

            dTextPltXYRect dictionary contains the ids which should be plotted
            as well as how many sets of rectangles related to that id to plot.

            the logic stores the current use counter related to the id within the
            list associated with that given id in this dictionary.

            With this one can limit the rectangles to be plotted to a subset
            and inturn how many rectangles related to it to plot.

            NOTE: with help from plotxy and textxy this is used to plot selective
            columns' data points' text legend/label's overlap check area.
            """
        if idCheck in self.dTestPlotXYRect:
            if self.dTestPlotXYRect[idCheck][0] < self.dTestPlotXYRect[idCheck][1]:
                print("DBUG:AnalPlot:TestPlotXYRect:{}:{}:{}".format(idCheck,sMsgT,sMsgB))
                self._test_plotxy_rect(ax, x1, y1, x2, y2, xscale, yscale, sMsgT, sMsgB)
                self.dTestPlotXYRect[idCheck][0] += 1


    def _mindelta_selfORextent(self, val, extent, ratio):
        delta = np.abs(val)*ratio
        if delta > extent*ratio:
            delta = extent*ratio
        return delta


    def axis_adjust(self, ax, dX, dY, xscale, yscale):
        if self.dbgAxisAdjustCntr > 0:
            print("DBUG:AnalPlot:_textxy:axis:1:{}".format(ax.axis()))
        tXMin = np.min(dX)
        tYMin = np.min(dY)
        tXMax = np.max(dX)
        tYMax = np.max(dY)
        if self.dbgAxisAdjustCntr > 0:
            print("DBUG:AnalPlot:_textxy:axis:2:{} {} {} {}".format(tXMin, tXMax, tYMin, tYMax))
        tRatio = 0.1
        tXRange = tXMax - tXMin
        tYRange = tYMax - tYMin
        if xscale == "log":
            tXMin -= self._mindelta_selfORextent(tXMin, tXRange, tRatio)
            tXMax += self._mindelta_selfORextent(tXMax, tXRange, tRatio)
            tYMin -= self._mindelta_selfORextent(tYMin, tYRange, tRatio)
            tYMax += self._mindelta_selfORextent(tYMax, tYRange, tRatio)
        else:
            tXMin -= tRatio*tXRange
            tXMax += tRatio*tXRange
            tYMin -= tRatio*tYRange
            tYMax += tRatio*tYRange
        ax.set_xlim(tXMin, tXMax)
        ax.set_ylim(tYMin, tYMax)
        if self.dbgAxisAdjustCntr > 0:
            print("DBUG:AnalPlot:_textxy:axis:3:{}".format(ax.axis()))
        self.dbgAxisAdjustCntr -= 1


    def _textxy_checkoverlap(self, ax, curLoc, curX, curY, curTxt, dX, dY, xscale, yscale, textOrientation="horizontal"):
        """ Check if the given location (curX,curY) for the given curTxt is ok
            or if it overlaps with any other text, whose x and y locations are
            passed using dX and dY arrays.

            xscale and yscale tell if the x or y axis is using linear or log
                based scale and inturn based on it, it adjusts calculations.

            TODO: Have to look at the current mapping/calc btw the xRange and yRange of
                data being plotted and the screen space it occupies and based on that
                adjust the area checked, Need to check if finetuning required for
                this logic like get char pixel size from default font or aspect
                ratio or ...
            """
        self.axis_adjust(ax, dX, dY, xscale, yscale)
        xMin, xMax, yMin, yMax = ax.axis()
        xRange = xMax-xMin
        yRange = yMax-yMin
        if xscale == "log":
            theX = np.log10(dX)
            tX = np.log10(curX)
            xRange = np.log10(xRange)
        else:
            theX = dX
            tX = curX
        if yscale == "log":
            theY = np.log10(dY)
            tY = np.log10(curY)
            yRange = np.log10(yRange)
        else:
            theY = dY
            tY = curY
        self.textxyXRange = xRange
        self.textxyYRange = yRange
        xDiff = theX-tX
        yDiff = theY-tY
        bbox = ax.get_window_extent()
        if self.dbgAxisAdjustCntr == 0:
            print("DBUG:AnalPlot:textxy:bbox",bbox)
        self.textxyCharPixRatioX = CHAR_XPIXELS/bbox.width
        self.textxyCharPixRatioY = CHAR_YPIXELS/bbox.height

        charPlotDataWidth = (xRange/bbox.width)*CHAR_XPIXELS
        charPlotDataHeight = (yRange/bbox.height)*CHAR_YPIXELS
        if textOrientation == "horizontal":
            deltaX = charPlotDataWidth * len(curTxt)
        else:
            deltaX = charPlotDataWidth * CHAR_NONORIENTATION_MULT
        if textOrientation == "vertical":
            deltaY = charPlotDataHeight * len(curTxt)
        else:
            deltaY = charPlotDataHeight * CHAR_NONORIENTATION_MULT
        dprint("DBUG:AnalPlot:textxy:tX={},tY={}, delta=x{}y{}".format(tX,tY,deltaX,deltaY))
        sMsgT = "xD={},xR={},xW={}".format(np.round(deltaX,4), np.round(xRange,4), np.round(bbox.width))
        sMsgB = "yD={},yR={},yW={}".format(np.round(deltaY,4), np.round(yRange,4), np.round(bbox.height))
        self.test_plotxy_rect(ax, curTxt, tX-deltaX, tY-deltaY, tX+deltaX, tY+deltaY, xscale, yscale, sMsgT, sMsgB)
        xConflict = np.argwhere( (xDiff > -deltaX) & (xDiff < deltaX) )
        yConflict = np.argwhere( (yDiff > -deltaY) & (yDiff < deltaY) )

        tList = []
        for xC in xConflict:
            tC = np.argwhere(yConflict == xC)
            dprint("xC:{}, tC:{}".format(xC, tC))
            if (len(tC) > 0):
                tList.append(xC[0])
        tList = np.array(tList)
        tList = tList[(tList != curLoc)]
        if (len(tList) > 0):
            dprint("DBUG:AnalPlot:textxy:{}:\ndX:{}\ndY:{}\nxDiff:{}\nyDiff:{}\nxConflict:{}\nyConflict:{}\ndeltaX{},deltaY{}; xRange{},yRange{}; bboxWidth{},bboxHeight{}"
                .format(curTxt,theX,theY,xDiff,yDiff,xConflict,yConflict,deltaX,deltaY,xRange,yRange,bbox.width,bbox.height))
            return True, tX, tY, tList
        return False, tX, tY, tList


    def _textxy(self, ax, curLoc, curX, curY, curTxt, dX, dY, xscale, yscale, textOrientation="horizontal"):
        """ Check if the given location (curX,curY) for the given curTxt is ok
            or if it overlaps with any other text, whose x and y locations are
            passed using dX and dY arrays.
            If it appears to overlap, then find a new location for curTxt.

            xscale and yscale tell if the x or y axis is using linear or log
                based scale and inturn based on it, it adjusts calculations.

            NOTE: This doesnt check if the new x and y position identified is ok
                or if it will overlap any existing text. This check is done by
                the following _textxy_super function below.
            """
        overlap,tX,tY,tList = self._textxy_checkoverlap(ax, curLoc, curX, curY, curTxt, dX, dY, xscale, yscale, textOrientation)
        if overlap:
            dprint("DBUG:AnalPlot:textxy:{}: tx {}, ty {}: tList {}".format(curTxt, tX, tY, tList))
            tX, tY = self.__newxy_rotate(ax, tX, tY, "seq")
            dprint("\tNew: {}, {}".format(tX, tY))
            if xscale == "log":
                curX = 10**tX
            else:
                curX = tX
            if yscale == "log":
                curY = 10**tY
            else:
                curY = tY
        else:
            dprint("DBUG:AnalPlot:textxy:{}: tx {}, ty {}: tList {}".format(curTxt, tX, tY, tList))
        return curX, curY


    def _textxy_super(self, ax, curLoc, curX, curY, curTxt, dX, dY, xscale, yscale):
        """ Helps check if the new value calculated by _textxy overlaps any other existing text
            or not. If it overlaps, then tries to identify a new location by calling _textxy
            again.

            NOTE: The logic attempts to find a new location only for a finite amount of time,
                if a suitable new location is not found, then it returns the original x and y
                position itself back.
                If the other overlapping text has still not been plotted, then there is still a
                small possibility that it may be moved for it overlapping with some text and this
                overlap also gets avoided due to that reason.
                Do note that the logic checks only to see if the current text overlaps the start
                location of any other texts and a rough area around it and not the full extent of
                those other texts, so this is not perfect. Also as already mentioned, if the
                overlapping text had already been plotted, then this small possibility of avoiding
                overlapping eitherway is not going to occur.
            """
        lastX = curX
        lastY = curY
        self.newxyRot = 0
        bRetainSame = True
        for i in range(4096):
            nX, nY = self._textxy(ax, curLoc, lastX, lastY, curTxt, dX, dY, xscale, yscale)
            overlap, tX, tY, tList = self._textxy_checkoverlap(ax, curLoc, nX, nY, curTxt, dX, dY, xscale, yscale)
            if not overlap:
                return nX, nY
            if bRetainSame:
                lastX = curX
                lastY = curY
            else:
                lastX = nX
                lastY = nY
        print("DBUG:AnalPlot:textxy_super:%s: Failed finding suitable new xy"%(curTxt), file=sys.stderr)
        return curX, curY


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
        self.dTestPlotXYRect = { 'FR': [0, 1], 'MP': [0, 1] }
        dX, dCHX, dRHX = self.get_data_selective(dataKeyX, plotSelCols)
        dY, dCHY, dRHY = self.get_data_selective(dataKeyY, plotSelCols)
        ax.plot(dX[selRow,:], dY[selRow,:], ".")
        print("DBUG:AnalPlot:plotxy:Cols %s"%(dCHX))
        if plotLegend != None:
            textDX = dX[selRow,:]
            textDY = dY[selRow,:]
            for i in range(len(dCHX)):
                tX = dX[selRow,i]
                tY = dY[selRow,i]
                tTxt = dCHX[i]
                tNX, tNY = self._textxy_super(ax, i, tX, tY, tTxt, textDX, textDY, xscale, yscale)
                textDX[i] = tNX
                textDY[i] = tNY
                ax.arrow(tX,tY, (tNX-tX), (tNY-tY), color=(1,0,0)).set_alpha(0.3)
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
