#!/usr/bin/env python3
# Covid19 AnalToolkit
# v20200429IST2053, HanishKVC
#

import sys
import datasrc as ds
import analplot
import matplotlib.pyplot as plt



dsEU = ds.EUWorldDataSrc()
dsC19In = ds.Cov19InDataSrc()

ap = analplot.AnalPlot()

fig, axes = plt.subplots(4,2)
iCur = 0
for ds in [ dsC19In, dsEU ]:
    ds.fetch_data()
    ds.load_data()
    ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr)
    ap.plot(axes[0,iCur], "raw")
    ap.calc_rel2mean()
    ap.plot(axes[1,iCur], "raw.rel2mean")
    ap.calc_rel2sum()
    ap.plot(axes[2,iCur], "raw.rel2sum")
    ap.calc_movavg()
    ap.plot(axes[3,iCur], "raw.movavg")
    iCur += 1

plt.show()


# vim: set softtabstop=4 expandtab shiftwidth=4: #
