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
