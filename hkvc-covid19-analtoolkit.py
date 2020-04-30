#!/usr/bin/env python3
# Covid19 AnalToolkit
# v20200429IST2053, HanishKVC
#

import sys
import datasrc as ds
import analplot
import matplotlib.pyplot as plt
import numpy as np



dsEU = ds.EUWorldDataSrc()
dsC19In = ds.Cov19InDataSrc()

ap = analplot.AnalPlot()

fig, axes = plt.subplots(4,2)
iCur = 0
sGlobalMsg = ""
for ds in [ dsC19In, dsEU ]:
    ds.fetch_data()
    ds.load_data()
    ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr)
    ap.plot(axes[0,iCur], "raw", numXTicks=4, xtickMultOf=7)
    ap.calc_rel2mean()
    ap.plot(axes[1,iCur], "raw.rel2mean")
    ap.calc_rel2sum()
    ap.plot(axes[2,iCur], "raw.rel2sum")
    ap.calc_movavg()
    selCols = ap.selcols_percentiles("raw.movavg")
    ap.plot(axes[3,iCur], "raw.movavg", plotSelCols=selCols)
    sGlobalMsg += " {}:DataDate:{}-{};".format(ds.name, np.min(ds.data[:,0]), np.max(ds.data[:,0]))
    iCur += 1

sGlobalMsg += " hkvc"
fig.text(0.01, 0.002, sGlobalMsg)
fig.set_tight_layout(True)
tFName = sGlobalMsg.replace(";","_N_").replace(" ","_")
fig.savefig("/tmp/{}.svg".format(tFName))
plt.show()


# vim: set softtabstop=4 expandtab shiftwidth=4: #
