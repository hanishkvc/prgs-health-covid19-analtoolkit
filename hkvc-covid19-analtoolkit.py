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

for ds in [ dsC19In, dsEU ]:
    ds.fetch_data()
    ds.load_data()
    ap.set_raw(ds.data[:,2:], ds.data[:,0], ds.hdr)
    ap.plot(plt, "raw")
    plt.show()


# vim: set softtabstop=4 expandtab shiftwidth=4: #
