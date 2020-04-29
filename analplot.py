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


    def plot(self, ax, dataSel, plotSel=None, plotLegend=None, plotXTickGap=None):
        d = self.data[dataSel]
        dCH = self.data["{}ColHdr".format(dataSel)]
        dRH = self.data["{}RowHdr".format(dataSel)]
        ax.plot(d)
        if plotLegend != None:
            ax.legend(dCH)
        if plotXTickGap != None:
            ax.set_xticks(np.arange(0, dRH.shape[0], plotXTickGap))
            ax.set_xticklabels(dRH[0::plotXTickGap])


# vim: set softtabstop=4 shiftwidth=4 expandtab: #
