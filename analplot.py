#!/usr/bin/env python3
# Analyse Plot data sets
# v20200429IST1936, HanishKVC
# 

import numpy as np



class AnalPlot:


    def set_raw(self, data, rowHdr=None, colHdr=None, skipRowsTop=0, skipRowsBottom=-1, skipColsLeft=0, skipColsRight=-1):
        self.data = {}
        self.data["raw"] = data
        self.data["rawRowHdr"] = rowHdr
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


    def plot(self, ax, dataSel, plotSel=None, plotLegend=None, plotXTickGap=None):
        d = self.data[dataSel]
        dCH = self.data["{}ColHdr".format(dataSel)]
        dRH = self.data["{}RowHdr".format(dataSel)]
        if plotSel == None:
            tD = d
            tDCH = dCH
        else:
            tD = d[:,plotSel]
            tDCH = dCH[plotSel]
        ax.plot(tD)
        if plotLegend != None:
            ax.legend(tDCH)
        if plotXTickGap != None:
            ax.set_xticks(np.arange(0, dRH.shape[0], plotXTickGap))
            ax.set_xticklabels(dRH[0::plotXTickGap])


# vim: set softtabstop=4 shiftwidth=4 expandtab: #
