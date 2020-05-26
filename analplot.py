#!/usr/bin/env python3
# Analyse Plot data sets
# v20200522IST2114, HanishKVC
# LGPL
#

import numpy as np
from helpers import *
import sys



DATAOPSCHAINER='>'

DBG_PLOTXYRECT_MSG=False
DBG_TEXTXY=False

bAUTO_AXISADJUST=True

DEF_CHARXPIXELS=9
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
    """ AnalPlot allows one to store, process and plot datasets in multiple ways.

        One could either call the processing functions explicitly first and then
        inturn use that data in a plot or print or further processing. OR ELSE
        one can let AnalPlot to automatically call the required data operations
        on its own to get the required data, even chaining the data operations
        if required, provided the user refers to the datasets (i.e dataKeys) in
        predefined ways, when using them in a plot or print or another calculation
        or when getting the data ...

        This predefined notation is called the dataKey dataOpsChaining, because
        in AnalPlot one refers to data stored in it using dataKeys. And if one
        specifies the dataKey using the dataOpsChaining notation, then AnalPlot
        will automatically trigger the required data operations in the required
        order, if any of the intermediate or final dataset is not already
        available or calculated in the given AnalPlot instance.

        MyDataSet1>DataOp1>ADataOpWithArgs(Arg1=Val1,Arg2=Val2)>...>DataOpN

        Note that AnalPlot always caches the results of data operations supported
        by it internally using a user specified dataKey or else a auto generated
        dataKey (which follows the dataOpsChaining notation). By default it eats
        memory to gain on processing ;-)

        Implementation Note:
        get_data and inturn auto calc logic path checks if data is already available
        before triggering a data operation to generate the data if required. However
        if one calls the calc_???? function directly, it will redo its calculation
        even if the result data is already available.

        """


    def __init__(self):
        """ Initialise a new instance of AnalPlot class
            """
        self.new_dataset()


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
        if DBG_TEXTXY:
            self.dbgAxisAdjustCntr = 1
        else:
            self.dbgAxisAdjustCntr = 0


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

            NOTE: If row or col header is not specified, then a numerical
            one is automatically created, which counts from 0 to row or
            col size as required.
            """
        sDKey, sCHKey, sRHKey = self._get_datakeys(dataKey)
        self.data[sDKey] = data
        if type(rowHdr) == type(None):
            rowHdr = np.arange(data.shape[0])
        if type(colHdr) == type(None):
            colHdr = np.arange(data.shape[1])
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


    def get_data_selective(self, dataKey="raw", selCols=None, selRows=None):
        """ Return the specified data and its col and row headers
            ie similar to get_data, except that the returned cols
            correspond to (i.e limited to) specified cols only.
            selCols: gives a list which contains True or False
                corresponding to each col in the dataset.
                Cols with True corresponding to their position,
                will be selected to be returned.
            """
        d, dCH, dRH = self.get_data(dataKey)
        tD = d
        tDCH = dCH
        tDRH = dRH
        if type(selCols) != type(None):
            tD = tD[:,selCols]
            tDCH = tDCH[selCols]
        if type(selRows) != type(None):
            tD = tD[selRows,:]
            tDRH = tDRH[selRows]
        return tD, tDCH, tDRH


    def print_data_selective(self, dataKey="raw", selCols=None):
        tD, tDCH, dRH = self.get_data_selective(dataKey, selCols)
        print("DBUG:AnalPlot:print_data:%s:%s"%(dataKey, selCols))
        print("DBUG:AnalPlot:print_data:ColHdr:\n",tDCH)
        print("DBUG:AnalPlot:print_data:Data:\n",tD)


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


    def get_rows_withval(self, dataKey="raw", val = 0):
        """ Find rows which contain the given val in all its cols
            """
        d, dCH, dRH = self.get_data(dataKey)
        rowsWithGivenValOnly = []
        for i in range(d.shape[0]):
            tMin = np.min(d[i,:])
            tMax = np.max(d[i,:])
            if (tMin == val) and (tMax == val):
                rowsWithGivenValOnly.append(i)
        return rowsWithGivenValOnly


    def _outdatakey(self, outDataKey, autoKey, inDataKey):
        """ return a outDataKey given the controlling parameters
            outDataKey: This could either be a explicit keyname to use
                or else it can be __AUTO__. If auto, then inDataKey
                and autoKey are concatenated together with a dot inbtw.
            autoKey: The keyname to suffix to inDataKey, if __AUTO__
                is specified for outDataKey.
            inDataKey: the inDataKey which corresponds to the input data
                to operate on by the calc_??? functions.
            """
        if outDataKey == "__AUTO__":
            theOutDataKey = "%s%s%s"%(inDataKey, DATAOPSCHAINER, autoKey)
        else:
            theOutDataKey = outDataKey
        return theOutDataKey


    def _call_calc_rel2mean(self, inDataKey, outDataKey, lArgNames, lArgVals):
        """ Helper routine to call calc_rel2mean; related to dataKey DataOpsChaining
            """
        axis = 0
        for arg in lArgNames:
            if (arg == "axis") or (arg == "A"):
                axis = int(lArgVals[lArgNames.index(arg)])
            else:
                print("WARN:AnalPlot:callCalcRel2Mean:Unknown arg[%s]"%(arg))
        self.dCalcFuncsWithArgs['rel2mean'][0](self, dataKey=inDataKey, outDataKey=outDataKey, axis=axis)


    def calc_rel2mean(self, dataKey="raw", bHandleRowsOrColsWith0=True, outDataKey="__AUTO__", axis=0):
        """ Calculate the mean for each row or col in the dataset and
            store the result of val/respective_mean for each value

            axis=0: Calc val/mean for each column.
            axis=1: Calc val/mean for each row.

            bHandleRowsOrColsWith0=True: Rows or Cols which contain only 0 in them
                retain the same after rel2mean is calculated. Whether it applies to
                rows or columns depends on if axis is 1 or 0.
                Without this such rows or cols will become nan.
            """
        d, dCH, dRH = self.get_data(dataKey)
        if bHandleRowsOrColsWith0:
            if axis == 0:
                colsWith0 = self.get_cols_withval(dataKey, 0)
            else:
                rowsWith0 = self.get_rows_withval(dataKey, 0)
        theOutDataKey = self._outdatakey(outDataKey, "rel2mean", dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys(theOutDataKey)
        if bHandleRowsOrColsWith0:
            if axis == 0:
                self.data[newDKey] = d/np.mean(d, axis=axis)
                self.data[newDKey][:,colsWith0] = 0
            else:
                self.data[newDKey] = d/np.mean(d, axis=axis).reshape(d.shape[0],1)
                self.data[newDKey][rowsWith0,:] = 0
        self.data[newRHKey] = dRH
        self.data[newCHKey] = dCH


    def _call_calc_rel2sum(self, inDataKey, outDataKey, lArgNames, lArgVals):
        """ Helper routine to call calc_rel2sum; related to dataKey DataOpsChaining
            """
        axis = 0
        for arg in lArgNames:
            if (arg == "axis") or (arg == "A"):
                axis = int(lArgVals[lArgNames.index(arg)])
            else:
                print("WARN:AnalPlot:callCalcRel2Sum:Unknown arg[%s]"%(arg))
        self.dCalcFuncsWithArgs['rel2sum'][0](self, dataKey=inDataKey, outDataKey=outDataKey, axis=axis)


    def calc_rel2sum(self, dataKey="raw", bHandleRowsOrColsWith0=True, outDataKey="__AUTO__", axis=0):
        """ Calculate the sum for each row or col in the dataset and
            store value/respective_rowOrCol_sum for each value in the dataset.

            axis=0: Calc val/sum for each column.
            axis=1: Calc val/sum for each row.

            bHandleRowsOrColsWith0=True: Rows or Cols which contain only 0 in them
                retain the same after rel2mean is calculated. Whether it applies to
                rows or columns depends on if axis is 1 or 0.
                Without this such rows or cols will contain nan in them.
            """
        d, dCH, dRH = self.get_data(dataKey)
        if bHandleRowsOrColsWith0:
            if axis == 0:
                colsWith0 = self.get_cols_withval(dataKey, 0)
            else:
                rowsWith0 = self.get_rows_withval(dataKey, 0)
        theOutDataKey = self._outdatakey(outDataKey, "rel2sum", dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys(theOutDataKey)
        if bHandleRowsOrColsWith0:
            if axis == 0:
                self.data[newDKey] = d/np.sum(d, axis=0)
                self.data[newDKey][:,colsWith0] = 0
            else:
                self.data[newDKey] = d/np.sum(d, axis=1).reshape(d.shape[0],1)
                self.data[newDKey][rowsWith0,:] = 0
        self.data[newRHKey] = dRH
        self.data[newCHKey] = dCH


    def _call_calc_scale(self, inDataKey, outDataKey, lArgNames, lArgVals):
        """ Helper routine to call calc_scale related to dataKey DataOpsChaining
            """
        axis = 0
        for arg in lArgNames:
            if (arg == "axis") or (arg == "A"):
                axis = int(lArgVals[lArgNames.index(arg)])
            else:
                print("WARN:AnalPlot:callCalcScale:Unknown arg[%s]"%(arg))
        self.dCalcFuncsWithArgs['scale'][0](self, dataKey=inDataKey, outDataKey=outDataKey, axis=axis)


    def calc_scale(self, dataKey="raw", outDataKey="__AUTO__", inMin=None, inMax=None, outMin=0, outMax=1, axis=0):
        """ Scale the data from inMin-inMax to outMin-outMax for each
            row (axis=1) or column (axis=0) in the specified input data
            dataKey: use data saved in/under this key, as the input data to scale
            outDataKey: save result in/using this key
                if "__AUTO__": then actual outDataKey is dataKey.scale
                else: outDataKey itself is the actual outDataKey
            inMin: Use this as the min value for respective input data cols
                None: Get min from the data cols itself
                a int value: Use this as the min for each data col
                a 1d-array: Use this as the min for each data col
            inMax: Use this as the max value for respective input data cols
            outMin: Use this as the min value for respective output data cols
            outMax: Use this as the max value for respective output data cols
            axis: Whether to operate on data across rows or columns in the dataset
                0: operate on data across rows, i.e on each column of data
                1: operate on data across cols, i.e on each row of data
            NOTE: this can work on a 2D data set, inturn on its rows or cols.
            """
        d, dCH, dRH = self.get_data(dataKey)
        if inMin == None:
            inMin = np.min(d, axis)
        elif type(inMin) == type(int()):
            inMin = np.ones(d.shape[1-axis])*inMin
        if inMax == None:
            inMax = np.max(d, axis)
        elif type(inMax) == type(int()):
            inMax = np.ones(d.shape[1-axis])*inMax
        if outMin == None:
            outMin = 0
        if type(outMin) == type(int()):
            outMin = np.ones(d.shape[1-axis])*outMin
        if outMax == None:
            outMax = 1
        if type(outMax) == type(int()):
            outMax = np.ones(d.shape[1-axis])*outMax
        if axis==1:
            inMin = inMin.reshape(d.shape[0],1)
            inMax = inMax.reshape(d.shape[0],1)
            outMin = outMin.reshape(d.shape[0],1)
            outMax = outMax.reshape(d.shape[0],1)
        inRange = inMax-inMin
        outRange = outMax-outMin
        theOutDataKey = self._outdatakey(outDataKey, "scale", dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys(theOutDataKey)
        self.data[newDKey] = (((d-inMin)/inRange)*outRange)+outMin
        self.data[newRHKey] = dRH
        self.data[newCHKey] = dCH


    def _call_calc_diff(self, inDataKey, outDataKey, lArgNames, lArgVals):
        """ Helper routine to call calc_diff related to dataKey DataOpsChaining
            """
        axis = 0
        for arg in lArgNames:
            if (arg == "axis") or (arg == "A"):
                axis = int(lArgVals[lArgNames.index(arg)])
            else:
                print("WARN:AnalPlot:callCalcDiff:Unknown arg[%s]"%(arg))
        self.dCalcFuncsWithArgs['diff'][0](self, dataKey=inDataKey, outDataKey=outDataKey, axis=axis)


    def calc_diff(self, dataKey="raw", outDataKey="__AUTO__", axis=0):
        """ Calculate the diff between adjacent values in the dataset.
            axis=0: diff across adjacent elements in each column
            axis=1: diff across adjacent elements in each row
            dataKey: the key used to access the data to operate on.
            outDataKey: key used to identify/store the results of operation.
            NOTE: It can work with 2D datasets, either across its rows or cols
            """
        d, dCH, dRH = self.get_data(dataKey)
        theOutDataKey = self._outdatakey(outDataKey, "diff", dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys(theOutDataKey)
        self.data[newDKey] = np.diff(d, axis=axis)
        if axis == 0:
            self.data[newRHKey] = dRH[1:]
            self.data[newCHKey] = dCH
        else:
            self.data[newRHKey] = dRH
            self.data[newCHKey] = dCH[1:]


    def _call_calc_cumsum(self, inDataKey, outDataKey, lArgNames, lArgVals):
        """ Helper routine to call calc_cumsum related to dataKey DataOpsChaining
            """
        axis = 0
        for arg in lArgNames:
            if (arg == "axis") or (arg == "A"):
                axis = int(lArgVals[lArgNames.index(arg)])
            else:
                print("WARN:AnalPlot:callCalcCumSum:Unknown arg[%s]"%(arg))
        self.dCalcFuncsWithArgs['cumsum'][0](self, dataKey=inDataKey, outDataKey=outDataKey, axis=axis)


    def calc_cumsum(self, dataKey="raw", outDataKey="__AUTO__", axis=0):
        """ Calculate the cumsum across adjacent values in the dataset.
            axis=0: cumsum across adjacent elements in each column
            axis=1: cumsum across adjacent elements in each row
            dataKey: the key used to access the data to operate on.
            outDataKey: key used to identify/store the results of operation.
            NOTE: It can work with 2D datasets, either across its rows or cols
            """
        d, dCH, dRH = self.get_data(dataKey)
        theOutDataKey = self._outdatakey(outDataKey, "cumsum", dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys(theOutDataKey)
        self.data[newDKey] = np.cumsum(d, axis=axis)
        self.data[newRHKey] = dRH
        self.data[newCHKey] = dCH


    def calc_movavg_old(self, dataKey="raw", avgOver=7, outDataKey="__AUTO__", axis=0):
        """ Calculate sliding window averages for values in the dataset
            along each row (axis=1) or column (axis=0).
            avgOver: the sliding window size
            """
        d, dCH, dRH = self.get_data(dataKey)
        tWeight = np.ones(avgOver)/avgOver
        if axis == 0:
            dataConv = np.zeros((d.shape[0]-(avgOver-1),d.shape[1]))
            for i in range(0,d.shape[1]):
                dataConv[:,i] = np.convolve(d[:,i], tWeight, 'valid')
        else:
            dataConv = np.zeros((d.shape[0],d.shape[1]-(avgOver-1)))
            for i in range(0,d.shape[0]):
                dataConv[i,:] = np.convolve(d[i,:], tWeight, 'valid')
        theOutDataKey = self._outdatakey(outDataKey, "movavg", dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys(theOutDataKey)
        self.data[newDKey] = dataConv
        if axis == 0:
            self.data[newRHKey] = list(range(dataConv.shape[0]))
            self.data[newCHKey] = dCH
        else:
            self.data[newRHKey] = dRH
            self.data[newCHKey] = list(range(dataConv.shape[1]))


    def _call_calc_movavg(self, inDataKey, outDataKey, lArgNames, lArgVals):
        """ Helper routine to call calc_movavg related to dataKey DataOpsChaining

            OLD NOTE: default for times is 1, so that this logic can be also used
            to get the semantics of normal movavg call when no arguments are given.
            """
        axis = 0
        times = 1
        for arg in lArgNames:
            if (arg == "axis") or (arg == "A"):
                axis = int(lArgVals[lArgNames.index(arg)])
            elif (arg == "times") or (arg == "T"):
                times = int(lArgVals[lArgNames.index(arg)])
            else:
                print("WARN:AnalPlot:callCalcMovAvg:Unknown arg[%s]"%(arg))
        self.dCalcFuncsWithArgs['movavg'][0](self, dataKey=inDataKey, outDataKey=outDataKey, times=times, axis=axis)


    def calc_movavg(self, dataKey="raw", avgOver=7, times=1, bRoundToDeci8=True, outDataKey="__AUTO__", axis=0):
        """ Calculate sliding window averages for values in the dataset
            along each row (axis=1) or column (axis=0).
            avgOver: the sliding window size
            times: the number of times movavg should be applied to specified data
            bRoundToDeci8: this forces the values to be rounded down to 8 decimal
                places if required.
            """
        d, dCH, dRH = self.get_data(dataKey)
        tWeight = np.ones(avgOver)/avgOver
        dCur = d
        for time in range(times):
            if axis == 0:
                dataConv = np.zeros((dCur.shape[0]-(avgOver-1),dCur.shape[1]))
                for i in range(0,dCur.shape[1]):
                    dataConv[:,i] = np.convolve(dCur[:,i], tWeight, 'valid')
            else:
                dataConv = np.zeros((dCur.shape[0],dCur.shape[1]-(avgOver-1)))
                for i in range(0,dCur.shape[0]):
                    dataConv[i,:] = np.convolve(dCur[i,:], tWeight, 'valid')
            dCur = dataConv
        if bRoundToDeci8:
            dCur = np.round(dCur, 8)
        theOutDataKey = self._outdatakey(outDataKey, "movavg", dataKey)
        newDKey, newCHKey, newRHKey = self._get_datakeys(theOutDataKey)
        self.data[newDKey] = dCur
        indexDelta = int(((avgOver-1)*times)/2)
        if axis == 0:
            #self.data[newRHKey] = list(range(dataConv.shape[0]))
            self.data[newRHKey] = dRH[indexDelta:-indexDelta]
            self.data[newCHKey] = dCH
        else:
            self.data[newRHKey] = dRH
            #self.data[newCHKey] = list(range(dataConv.shape[1]))
            self.data[newCHKey] = dCH[indexDelta:-indexDelta]


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


    def selcols_colhdr(self, dataKey="raw", colIds=None):
        """ Select those Columns of given dataset named dataKey, whose column
            header names are given in colIds list

            If colIds is None, then all cols are selected.
            """
        d, dCH, dRH = self.get_data(dataKey)
        if colIds == None:
            return dCH == dCH
        selCols = []
        for curId in dCH:
            if curId in colIds:
                selCols.append(True)
            else:
                selCols.append(False)
        return(selCols)


    dCalcSimpleFuncs = {
    }
    dCalcFuncsWithArgs = {
        "scale": [calc_scale, _call_calc_scale],
        "diff": [calc_diff, _call_calc_diff],
        "cumsum": [calc_cumsum, _call_calc_cumsum],
        "movavg": [calc_movavg, _call_calc_movavg],
        "rel2mean": [calc_rel2mean, _call_calc_rel2mean],
        "rel2sum": [calc_rel2sum, _call_calc_rel2sum],
    }


    def get_data(self, dataKey="raw"):
        """ Return the specified data and its col and row headers
            Create them by calling required calc functions, if required and possible.

            NOTE: If data is already available, then return it. Only if it is not
            there, try to create it by assuming that the given dataKey follows
            dataKey dataOpsChaining notatation and inturn calling specified dataOps.
            """
        if dataKey in self.data:
            return self._get_data(dataKey)
        # This means data not in dict, lets see if we can create it
        [sBDKey, sCmd] = dataKey.rsplit(DATAOPSCHAINER,1)
        # Create using a simple calc func
        if sCmd in self.dCalcSimpleFuncs:
            self.dCalcSimpleFuncs[sCmd](self, sBDKey)
            return self._get_data(dataKey)
        # Handle funcs with arguments using the new syntax
        lTemp = sCmd.split('(',1)
        sFName = lTemp[0]
        if sFName in self.dCalcFuncsWithArgs:
            lArgNames = []
            lArgVals = []
            if len(lTemp) > 1:
                lTemp[1] = lTemp[1][:-1]
                sArgs = lTemp[1]
                lArgs = sArgs.split(',')
                for arg in lArgs:
                    lArgNames.append(arg.split('=')[0])
                    lArgVals.append(arg.split('=')[1])
            self.dCalcFuncsWithArgs[sFName][1](self, sBDKey, dataKey, lArgNames, lArgVals)
            return self._get_data(dataKey)
        # Dont understand the data ops function being refered
        raise NotImplementedError("AnalPlot:get_data:{}:Func[{}] not found...\n\tAvailable DataSets:{}".format(dataKey, sCmd, self.data.keys()))


    def del_data(self, dataKey, bDelDataDerivedFromThis=True):
        """ Remove the specified dataKey and its associated data and headers

            bDelDataDerivedFromThis = True: will also delete all data created
                by using the specified dataKey as the base in the dataOpsChaining,
                provided the dataKey names of all these data start with dataKey.
                This is the case if calc_????? functions are allowed to set the
                dataKey for their calculated data.

                NOTE: If some unrelated dataset is stored in the AnalPlot instance
                with a dataKey name whose starting part matchs the dataKey passed
                to del_data, then even it and its derived datasets will/can get
                deleted.

                NOTE: Not just the data, but also their associated col and row
                header data is also deleted.
            """
        sDKey, sCHKey, sRHKey = self._get_datakeys(dataKey)
        self.data.pop(sDKey)
        self.data.pop(sCHKey)
        self.data.pop(sRHKey)
        if bDelDataDerivedFromThis:
            tKeys = list(self.data.keys())
            for key in tKeys:
                if key.startswith(dataKey):
                    self.data.pop(key)
        dprint("DBUG:AnalPlot:del_data:%s:%s"%(dataKey, self.data.keys()))


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
        """ Boxplot the dataset selected using dataKey on the given plot axes ax.

            plotSelCols: The subset of cols to plot from the dataset. If not specified,
                then all cols from the dataset will be plotted.
            Title: the Title to assign for the current boxplot.
                If __AUTO__ is part of the title, it will be replaced with the dataKey.
            bInsetBoxPlot: If True, then the same data is also boxplotted in log scale,
                in a translucent manner on top of the original boxplot. This occupies
                the top half of the current plot axes.
            """
        tD, tDCH, dRH = self.get_data_selective(dataKey, plotSelCols)
        ax.boxplot(tD,labels=tDCH)
        if title != None:
            if title.find("__AUTO__") != -1:
                title = title.replace("__AUTO__", dataKey)
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

            dTestPlotXYRect dictionary contains the ids which should be plotted
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
        """ Adjust the data limits for the given plot axes's x and y
            axis, based on the min and max value in the list of x
            and y values to be plotted.

            When plotting on a log scale, the entry which corresponds
            to 0 in x or y axis may not be shown, because the new limit
            which is being set will keep 0 out of its plot window.
            """
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
            if tXMin == 0:
                tXMin = np.min(dX[dX>0])
                tXMin -= self._mindelta_selfORextent(tXMin, tXRange, tRatio)
            tXMax += self._mindelta_selfORextent(tXMax, tXRange, tRatio)
            tYMin -= self._mindelta_selfORextent(tYMin, tYRange, tRatio)
            if tYMin == 0:
                tYMin = np.min(dY[dY>0])
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
        if bAUTO_AXISADJUST:
            self.axis_adjust(ax, dX, dY, xscale, yscale)
        xMin, xMax, yMin, yMax = ax.axis()
        if xscale == "log":
            theX = np.log10(dX)
            tX = np.log10(curX)
            xRange = np.log10(xMax) - np.log10(xMin)
            tXMid = np.log10(xMin) + (xRange/2)
        else:
            theX = dX
            tX = curX
            xRange = xMax-xMin
            tXMid = xMin + (xRange/2)
        if yscale == "log":
            theY = np.log10(dY)
            tY = np.log10(curY)
            yRange = np.log10(yMax) - np.log10(yMin)
            tYMid = np.log10(yMin) + (yRange/2)
        else:
            theY = dY
            tY = curY
            yRange = yMax-yMin
            tYMid = yMin + (yRange/2)
        self.textxyXRange = xRange
        self.textxyYRange = yRange
        xDiff = theX-tX
        yDiff = theY-tY
        bbox = ax.get_window_extent()
        if self.dbgAxisAdjustCntr == 0:
            print("DBUG:AnalPlot:textxy:bbox",bbox)
            tXDelta = xRange/4
            tYDelta = yRange/4
            self._test_plotxy_rect(ax, tXMid-tXDelta, tYMid-tYDelta, tXMid+tXDelta, tYMid+tYDelta, xscale, yscale)
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


    def plotxy(self, ax, dataKeyX, dataKeyY, selRow=-1, plotSelCols=None, title="__AUTO__", xscale="linear", yscale="linear", plotLegend=None, bTranslucent=False,
                    colorControlVals=None, colorControlLimits=[0], colorMarkers=['ro','go']):
        """ Plot the specified subset of cols from two related datasets such that
            values of the selected row of these cols in one of the dataset acts as
            the x value and the values of the selected row of these cols in the
            other dataset acts as the y value.

            ax: the axes or inset in which to plot.
            dataKeyX: the dataset to use for X axis related values.
            dataKeyY: the dataset to use for Y axis related values.
            selRow: Specifies which row in the given x and y datasets' selected
                cols provides the x and y values for the xy plot.
            plotSelCols: list of cols which should be represented in the plot.
            title: None or title to plot. Specified title can contain "__AUTO__"
                __AUTO__ in title replaced by string "<dataKeyX> vs <dataKeyY>"

            Controlling color of Markers:
            The array colorControlVals, contains values which control what color
            to show based on where they fit wrt the colorControlLimits array.

            The vals may fall into groups as discussed below
                values LESSTHAN CCL[0]
                values WITHIN CCL[i] and CCL[i+1]; for each pair of values in CCL
                values GREATERTHAN CCL[-1]
            For each group the color and marker to use is given by colorMarkers
            """
        if DBG_TEXTXY:
            self.dTestPlotXYRect = { 'FR': [0, 1], 'BR': [0, 1] }
        else:
            self.dTestPlotXYRect = {}
        dX, dCHX, dRHX = self.get_data_selective(dataKeyX, plotSelCols)
        dY, dCHY, dRHY = self.get_data_selective(dataKeyY, plotSelCols)
        if type(colorControlVals) == type(None):
            ax.plot(dX[selRow,:], dY[selRow,:], ".")
        else:
            cCV = np.array(colorControlVals)
            theColors = np.zeros(len(cCV))
            print("DBUG:AnalPlot:plotxy:cCV {}, cCL {} ".format(colorControlVals, colorControlLimits))
            for iColor in range(len(colorControlLimits)):
                theColors[cCV > colorControlLimits[iColor]] = iColor+1
            print("DBUG:AnalPlot:plotxy:theColors:{}".format(theColors))
            #list(map(lambda x,y,iC: ax.plot(x,y,colorMarkers[int(iC)]), dX[selRow,:], dY[selRow,:], theColors))
            for  x,y,iC in zip(dX[selRow,:], dY[selRow,:], theColors):
                ax.plot(x,y,colorMarkers[int(iC)])
        #ax.scatter(dX[selRow,:], dY[selRow,:])
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
                aXDelta = tNX-tX
                aYDelta = tNY-tY
                print("DBUG:AnalPlot:plotxy:arrow:{}:{},{} to {},{}; {},{}".format(tTxt,tX,tY,tNX,tNY,aXDelta,aYDelta))
                if not ((aXDelta == 0.0) and (aYDelta == 0.0)):
                    ax.arrow(tX,tY, aXDelta, aYDelta, color=(0,0,1)).set_alpha(0.3)
                ax.text(tNX, tNY, tTxt)
        if title != None:
            if title.find("__AUTO__") != -1:
                sAuto = "X%sVsY%s"%(dataKeyX, dataKeyY)
                title = title.replace("__AUTO__", sAuto)
            ax.set_title(title)
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        if bTranslucent:
            ax.set_facecolor([1,1,1,0.1])
            for l in ax.lines:
                l.set_alpha(0.4)
            ax.tick_params(color=[0,0,0,0.4], labelcolor=[0,0,0,0.4], which="both")
            ax.title.set_alpha(0.4)
            for t in ax.texts:
                t.set_alpha(0.4)


    def groupsimple_percentiles(self, dataKey, selCols=None, selRows=None, dataOps='movavg', percentileRange=[70,100], tempBaseKey="_T_GSP_"):
        """ Group the specified subset of data from the specified data set
            into few groups based on the simple criteria of percentiles.
            dataKey: the base data set to work on
            selCols: the list of cols which belong to the specified subset
            selRows: the list of rows which belong to the specified subset
            dataOps: dataKey dataOpsChaining notation based set of operations
                to apply on the selected subset of data.
            percentileRange: select columns which fall into the specified
                range of percentiles, from the selected subset of data, by
                applying percentile on the results of the dataOps on that
                selected subset of data.

            So put in a simple way:
            For the specified dataset, first select a subset of rows and cols,
            next apply the specified dataOps, lastly select the cols which
            belong to the specified percentile range when the values of the
            last row are looked at.

            Returns: It returns info about selected cols which fall in the given
            percentile range in two formats.
            One list consisting of
                the list of corresponding/selected cols' column header values.
                the list of non selected cols' column header values.
            Another list which is numeric. For positions in selCols list, which
                correspond to cols in given percentile range, it will contain 1,
                and in other positions, it will caontain -1.
                i.e selColsInPercentileRange related positions have 1 and
                selColsOutsidePercentileRange related positions have -1
                NOTE that this list is limited to selCols only and not all the
                cols in the given dataKey.

            NOTE: it uses _T_GSP_ and associated dataOpsChaining as a temporary
            dataKey namespace for its internal operations, by default. User can
            change this by setting the tempBaseKey argument, if required.
            """
        d, dCH, dRH = self.get_data_selective(dataKey, selCols, selRows)
        self.set_raw(d, rowHdr=dRH, colHdr=dCH, dataKey=tempBaseKey)
        dOpsKey = "%s>%s"%(tempBaseKey, dataOps)
        oD, oCH, oRH = self.get_data(dOpsKey)
        selColsP, selPers = self.selcols_percentiles(dOpsKey, selPers=percentileRange)
        dprint("DBUG:AnalPlot:groupsimple_percentiles:selColsP:{}".format(selColsP))
        selColsPNumBased = np.ones(len(selColsP))
        selColsPNumBased[~selColsP] = -1
        self.del_data(tempBaseKey)
        return [oCH[selColsP], oCH[~selColsP]], selColsPNumBased


    def _localcenters_neighboursDist(self, theX, theY, theDist):
        lX, lY = [], []
        for x,y in zip(theX, theY):
            dist = np.sqrt((theX-x)**2 + (theY-y)**2)
            grpX = theX[dist<theDist]
            grpY = theY[dist<theDist]
            gxMin, gxMax = np.min(grpX), np.max(grpX)
            gyMin, gyMax = np.min(grpY), np.max(grpY)
            tX = np.mean([gxMin, gxMax])
            tY = np.mean([gyMin, gyMax])
            lX.append(tX)
            lY.append(tY)
        return np.array(lX), np.array(lY)


    def groupsimple_neighbours(self, dataKeyX, dataKeyY, selCols=None, selRows=None, diagRatio=0.25, ax=None):
        """ Group the specified subset of data from the given dataset into few groups
            based on how near they are to one another, based on the values in the
            two specified subsets.

            dataKeyX, dataKeyY: specify the datasets to use for x and y axis. Or put
                differently are the values of two parameters for a set of objects of
                the study, which are being relatively compared among themselves as
                well as between them.
            selCols, selRows: allows one to use a subset of the given dataset, for
                grouping. The other rows and cols of the datasets are ignored while
                comparing and grouping. If there are more than 1 row, in the subset,
                then the last row's data will be used for comparision and grouping.

            diagRatio: the ratio of total data bounding rectangle diagonal distance,
                which is used to decide whether two pointsOfInterest are neighbours
                or not. Smaller the ratio more the groups, larger the ratio less the
                number of groups into which the data is segregated/grouped.

            ax: a plot axes, which can be used to look at a visual view/debug of the
                underlying logic.

            NOTE1: Now the local centers identified are cross-checked to see if they
            are near enough to merge into a new local center. And this testis done,
            till we no longer get new collased/merged local centers.

            However this also has the side-effect that, local centers can move away
            from the edges, through merging. And this can in some cases, lead to the
            edge point(s) becoming nearer and inturn assigned to a previously unrelated
            but relatively speaking near in a way local center.

            NOTE2: The cols of the given datasets are the anchors/entities/objects
            being studied. Each dataset is the values of some property(s) relating to
            them. All rows could represent the values of the same property or values
            of different properties or values of some operation(s) on property(s).
            """
        # 1. The data subset to work on
        dX, dXCH, dXRH = self.get_data_selective(dataKeyX, selCols, selRows)
        dY, dYCH, dYRH = self.get_data_selective(dataKeyY, selCols, selRows)
        theX = dX[-1,:]
        theY = dY[-1,:]
        if ax != None:
            ax.plot(theX,theY, "ro")
            print("DBUG:AnalPlot:GSNeighbours:theX,theY:{}".format(list(zip(theX, theY))))
        # 2. Find local centers
        # The data space adjusted base distance for neighbours to start with
        xMin, xMax = np.min(theX), np.max(theX)
        yMin, yMax = np.min(theY), np.max(theY)
        curDist = np.sqrt((xMax-xMin)**2 + (yMax-yMin)**2)*diagRatio
        if ax != None:
            print("DBUG:AnalPlot:GSNeighbours:xMin,xMax {},{}:yMin,yMax {},{}:curDist {}".format(xMin,xMax,yMin,yMax,curDist))
        # get the local centers, corresponding to each point of interest
        lcX,lcY = self._localcenters_neighboursDist(theX, theY, curDist)
        if ax != None:
            ax.plot(lcX,lcY, "g*")
            print("DBUG:AnalPlot:GSNeighbours:Initial lcX,lcY:{}".format(list(zip(lcX, lcY))))
        # consolidate local centers, in case they are near to one another.
        # Currently I am not giving weightage to the initial local centers
        # based on how many neighbours it might have. Have to think about
        # this bit more later.
        iPrevGrps, iCurGrps = -2, -1
        while iPrevGrps != iCurGrps:
            iPrevGrps = iCurGrps
            lcX,lcY = self._localcenters_neighboursDist(lcX, lcY, curDist*1.2)
            lc = np.array(list(zip(lcX, lcY)))
            lc = np.unique(lc, axis=0)
            iCurGrps = len(lc)
            print("DBUG:AnalPlot:GSNeighbours:lc:{}".format(lc))
        if ax != None:
            ax.plot(lcX,lcY, "b.")
            ax.axis('square')
            ax.set_xlim(-10,10)
            ax.set_ylim(-10,10)
        # 3. Map each point of interest(i.e a col in the selected subset)
        # to its nearest local center
        lGroup = []
        for x,y in zip(theX, theY):
            dist = np.sqrt((lc[:,0]-x)**2 + (lc[:,1]-y)**2)
            lGroup.append(np.argwhere(dist == np.min(dist))[0][0])
        return lc, lGroup


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



def test_data_simple():
    """ Generate a very simple test data based instance of AnalPlot
        """
    ap=AnalPlot()
    ap.set_raw(np.arange(20).reshape(5,4))
    return ap



def test_groupsimple_neighbours():
    fig, axes = ap.subplots(plt, 2, 2)
    lc, colorControlVals = ap.groupsimple_neighbours('MyData>movavg', 'MyData', selCols=None, selRows=None, ax=axes[1,0])
    print(lc, colorControlVals)
    ap.plotxy(axes[0,0], 'MyData>movavg', 'MyData', colorControlVals=colorControlVals, colorControlLimits=list(range(len(lc))),
                colorMarkers=['ro','r*','r.','yo','y*','y.','b.','b*','bo','g.','g*','go'][:len(lc)])
    fig.savefig('/tmp/analplot_test2.png')
    plt.show()



if __name__ == "__main__":

    import matplotlib.pyplot as plt

    sTestData = "default"
    if len(sys.argv) > 1:
        sTestData = sys.argv[1]
    # Autocalling of operations like done below use default values
    # for the respective operation/function arguments
    # As movavg by default avgs over a window of 7 data values
    # and inturn retains only those values which could use the
    # full span of avging window, so data size needs to be large enough
    if sTestData == "--0_200":
        t1 = np.arange(0,200).reshape(20,10)
    elif sTestData == "--ones":
        t1 = np.ones(200).reshape(20,10)
    else:
        t1 = np.random.uniform(-10,10,(20,10))
    ap = AnalPlot()
    ap.set_raw(t1,dataKey='MyData')
    fig, axes = ap.subplots(plt, 5, 2)
    # 1st column of plots
    ap.plot(axes[0,0], 'MyData', title="__AUTO__")
    ap.print_data_selective('MyData')
    ap.plot(axes[1,0], 'MyData>movavg', title="__AUTO__")
    ap.print_data_selective('MyData>movavg')
    ap.plot(axes[2,0], 'MyData>movavg(T=2)', title="__AUTO__")
    ap.plot(axes[3,0], 'MyData>rel2mean', title="__AUTO__")
    ap.print_data_selective('MyData>rel2mean')
    ap.plot(axes[4,0], 'MyData>rel2sum', title="__AUTO__")
    ap.print_data_selective('MyData>rel2sum')
    # 2nd column of plots
    ap.calc_scale('MyData', 'MyData>scaleA0', axis=0) # This should match autocalcd MyData>scale data
    ap.print_data_selective('MyData>scaleA0')
    ap.calc_scale('MyData', 'MyData>scaleA1', axis=1) # This should match autocalcd MyData>scale(axis=1) data
    ap.plot(axes[0,1], 'MyData>scale', title="__AUTO__")
    ap.print_data_selective('MyData>scale')
    ap.plot(axes[1,1], 'MyData>scale>movavg', title="__AUTO__")
    ap.plot(axes[2,1], 'MyData>scale(axis=1)', title="__AUTO__")
    ap.print_data_selective('MyData>scale(axis=1)')
    ap.plot(axes[3,1], 'MyData>scale(axis=1)>movavg', title="__AUTO__")
    # Some additional checks
    ap.print_data_selective('MyData')
    ap.calc_movavg('MyData', outDataKey='MyData>a1movavg', axis=1)
    ap.print_data_selective('MyData>a1movavg')
    # Save and Show plots
    fig.set_tight_layout(True)
    fig.savefig('/tmp/analplot_test1.png')
    plt.show()

    test_groupsimple_neighbours()



# vim: set softtabstop=4 shiftwidth=4 expandtab: #
