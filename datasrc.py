#
# DataSrc Base Class plus additional Classes
# v20200423IST2313, HanishKVC
#

import os
import time
import subprocess
import numpy
import sys
import calendar


class DataSrc:

    bTestForceMissing = False

    def fix_missing_localmean(self, axis=0, iNear=3):
        """ Fix missing value(s) using local mean among adjacent neighbours
            Supports 2D array
            """
        if self.bTestForceMissing:
            self.data[5,0] = numpy.NAN
        lNan = numpy.argwhere(numpy.isnan(self.data))
        for iCur in lNan:
            iS = iCur[axis] - iNear
            if iS < 0:
                iS = 0
            iE = iCur[axis] + iNear + 1
            if iE > self.data.shape[axis]:
                iE = self.data.shape[axis]
            if axis == 0:
                tData = self.data[iS:iE, iCur[1]]
            else:
                tData = self.data[iCur[0], iS:iE]
            self.data[tuple(iCur)] = 0
            iMean = numpy.sum(tData)/(iE-iS-1)
            print("INFO:DataSrc:fix_missing:pos={}:curarea={}:new={}".format(iCur, tData, iMean))
            self.data[tuple(iCur)] = iMean


    def download(self, theUrl = None, localFileName = None):
        if theUrl == None:
            theUrl = self.url
        if localFileName == None:
            localFileName = self.localFileName
        print("INFO:DataSrc:{}:downloading...".format(theUrl))
        tCmd = [ "wget", theUrl, "--output-document={}"]
        tCmd[2] = tCmd[2].format(localFileName)
        if subprocess.call(tCmd) != 0:
            raise ConnectionError("DataSrc:{}: Download data from net failed".format(theUrl))


    def _fix_url_filenames(self):
        raise NotImplementedError("DataSrc: Download data from net...")


    def _set_fetch_date(self, day, month, year):
        curTime = time.gmtime()
        if day == None:
            self.fd_day = curTime.tm_mday
        else:
            self.fd_day = day
        if month == None:
            self.fd_month = curTime.tm_mon
        else:
            self.fd_month = month
        if year == None:
            self.fd_year = curTime.tm_year
        else:
            self.fd_year = year


    def _fetch_data(self, day=None, month=None, year=None):
        self._set_fetch_date(day, month, year)
        self._fix_url_filenames()
        if os.path.exists(self.localFileName) and (os.path.getsize(self.localFileName)>128):
            print("INFO:DataSrc:{}:already downloaded".format(self.localFileName))
            return True
        self.download()


    def conv_xls2csv(self, xls, csv):
        # For now use as a program, later may change to use as a library
        tCmd = [ "./libs/hkvc_pyuno_toolkit/hkvc_pyuno_toolkit.py", "ss2csv", xls, csv ]
        if subprocess.call(tCmd) != 0:
            raise OSError("DataSrc:ConvXls2Csv:{}".format(tCmd))


    def _fetchconv_postproc(self):
        raise NotImplementedError("DataSrc:_fetchconv_postproc: of data fetched and or converted to csv...")


    def conv_data(self):
        if self.localFileType == "xls":
            xlsFN = self.localFileName
            (tBase, tExt) = os.path.splitext(xlsFN)
            csvFN = "{}.csv".format(tBase)
            self.conv_xls2csv(xlsFN, csvFN)
            self.localFileName = csvFN
            self.localFileType = "proc"

        if self.localFileType == "proc":
            self._fetchconv_postproc()


    def fetch_data(self, day=None, month=None, year=None):
        self._fetch_data(day, month, year)
        self.conv_data()


    def conv_date_str2int(self, sDate, delimiter="-", iY = 0, iM=1, iD=2, mType="int", bYear2Digit=False):
        sDate = sDate.decode('utf-8')
        sDate = sDate.split(delimiter)
        iDate = int(sDate[iY])*10000
        if bYear2Digit:
            iDate += 20000000
        if mType == "int":
            iDate += int(sDate[iM])*100
        else:
            iDate += list(calendar.month_abbr).index(sDate[iM])*100
        iDate += int(sDate[iD])
        return iDate


    def _load_hdr(self, fileName, delimiter, iHdrLine):
        f = open(fileName)
        i = 0
        for l in f:
            if (i == iHdrLine):
                return l.split(delimiter)
            i += 1
        raise ImportError("DataSrc:_load_hdr: No header found")


    def load_data(self, fileName=None, dtype=float, delimiter=None, skip_header=None, converters=None, iHdrLine=None, usecols=None):
        """
            iHdrLine: the column header line among the skip_header lines, starts at 0
            """
        if fileName == None:
            fileName = self.localFileName
        print("INFO:DataSrc:Loading:{}".format(fileName))
        self.data = numpy.genfromtxt(fileName, dtype = dtype, delimiter=delimiter, skip_header=skip_header, converters=converters, usecols=usecols)
        if (skip_header != None) and (iHdrLine != None):
            if (iHdrLine < skip_header):
                self.hdr = self._load_hdr(fileName, delimiter, iHdrLine)
            else:
                raise ImportError("DataSrc:load_data: HeaderLine {} >= SkipHeader {}".format(iHdrLine, skip_header))



class Cov19InDataSrc(DataSrc):

    #urlFmt = "http://api.covid19india.org/states_daily_csv/confirmed.csv"
    nwFileNameFmt = "confirmed.csv"
    urlFmt = "http://api.covid19india.org/states_daily_csv/{}"
    localFileNameFmt = "data/{}-{}{:02}{:02}-{}"

    def __init__(self):
        self.name = "Cov19In"


    def _fix_url_filenames(self):
        self.nwFileName = self.nwFileNameFmt
        self.url = self.urlFmt.format(self.nwFileName)
        self.localFileName = self.localFileNameFmt.format(self.name, self.fd_year, self.fd_month, self.fd_day, self.nwFileName)
        # fetched file is csv and has data in required way, so no need for postproc; so set to "csv"
        self.localFileType = "csv"


    def conv_date(self, sDate):
        return float(self.conv_date_str2int(sDate, iY=2, iD=0, mType="abbr", bYear2Digit=True))


    def load_data(self, fileName=None):
        converters = { 0: lambda x: self.conv_date(x) }
        super().load_data(fileName=fileName, delimiter=",", skip_header=1, converters=converters, iHdrLine=0)
        self.hdr = self.hdr[:-1]
        self.data = self.data[:,:-1]



class EUWorldDataSrc(DataSrc):

    #url="https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-2020-03-20.xlsx"
    nwFileNameFmt = "COVID-19-geographic-disbtribution-worldwide-{}-{:02}-{:02}.xlsx"
    urlFmt = "https://www.ecdc.europa.eu/sites/default/files/documents/{}"
    #localFileNameFmt = "data/{}-{}{:02}{:02}-{}"
    localFileNameFmt = "data/{}-{}{:02}{:02}.xlsx"

    def __init__(self):
        self.name = "EUWorld"
        self.fields = [ "dateRep", "cases", "geoId" ]
        self.geoIds = []


    def _fix_url_filenames(self):
        self.nwFileName = self.nwFileNameFmt.format(self.fd_year, self.fd_month, self.fd_day)
        self.url = self.urlFmt.format(self.nwFileName)
        self.localFileName = self.localFileNameFmt.format(self.name, self.fd_year, self.fd_month, self.fd_day)
        # fetched file is xlsx and also needs postproc; Set to "xls"
        self.localFileType = "xls"


    def conv_geoid(self, sGeoId):
        try:
            i = self.geoIds.index(sGeoId)
        except ValueError:
            self.geoIds.append(sGeoId)
            i = len(self.geoIds) - 1
        return i


    def _fetchconv_postproc(self):
        fIn = open(self.localFileName)
        fOutName = "{}.tmp".format(self.localFileName)
        fOut = open(fOutName, "w+")
        for l in fIn:
            if l.find('"') == -1:
                fOut.write(l)
                continue
            bInDQuote = False
            lOut = ""
            for c in l:
                if c == '"':
                    bInDQuote = not bInDQuote
                if bInDQuote and (c == ','):
                    c = '_'
                lOut += c
            fOut.write(lOut)
        fIn.close()
        fOut.close()
        os.rename(fOutName, self.localFileName)
        hdr = self._load_hdr(self.localFileName, ",", 0)
        cols = []
        for i in self.fields:
            cols.append(hdr.index(i))
        cols = tuple(cols)
        converters = { 0: lambda x: self.conv_date(x), cols[2]: lambda x: self.conv_geoid(x) }
        print(cols)
        super().load_data(fileName=fileName, dtype=int, delimiter=",", skip_header=1, converters=converters, iHdrLine=0, usecols=cols)
        print(self.data)
        input("DBG: CHeck postproc data")


    def conv_date(self, sDate):
        iDate = self.conv_date_str2int(sDate, delimiter="/", iY=2, iD=0, mType="int", bYear2Digit=False)
        fDate = float(iDate)
        #print(sDate, fDate)
        return iDate


    def load_data(self, fileName=None):
        super().load_data(fileName=fileName, delimiter=",", skip_header=1, iHdrLine=0)
        self.hdr = self.hdr[:-1]
        self.data = self.data[:,:-1]



if __name__ == "__main__":
    for theDataSrc in [ Cov19InDataSrc(), EUWorldDataSrc()]:
        fileName = None
        try:
            if len(sys.argv) == 1:
                theDataSrc.fetch_data()
            else:
                fileName = sys.argv[1]
        except ConnectionError as e:
            print("ERRR:{}".format(e))
            continue
        theDataSrc.load_data(fileName)
        print(theDataSrc.hdr)
        print(theDataSrc.data)
        theDataSrc.fix_missing_localmean()



# vim: set softtabstop=4 expandtab shiftwidth=4: #
