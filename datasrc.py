#
# DataSrc Base Class plus additional Classes
# v20200430IST1742, HanishKVC
# LGPL
#

import os
import time
import subprocess
import numpy
import sys
import calendar
from helpers import *



class DataSrc:
    """ The base class for downloading data and inturn loading the downloaded data
        into memory. User can use fetch_data and load_data for this.

        TO help with same child classes can implement
        _fix_url_filenames:
        _fetchconv_postproc:
        """

    bTestForceMissing = False

    def fix_missing_value(self, missing=numpy.NAN, value=0):
        """ Fix missing value(s) using the specified value
            missing: the value to be treated as missing value
            value: the value to use in place of missing value
            """
        if numpy.isnan(missing):
            lMissing = numpy.argwhere(numpy.isnan(self.data))
            self.data[numpy.isnan(self.data)] = value
        else:
            lMissing = numpy.argwhere(self.data == missing)
            self.data[self.data == missing] = value
        print("INFO:DataSrc:fix_missing_value:lMissing:", lMissing)
        return lMissing


    def fix_missing_localmean(self, missing=numpy.NAN, axis=0, iNear=3):
        """ Fix missing value(s) using local mean among adjacent neighbours
            Supports 2D array.
            missing: the value to be treated as missing value
            axis: specify which axis one should consider for neighbours.
                0: values across rows i.e in a given column
                1: values across cols i.e in a given row
            iNear: How many neighbours to use on either side of missing value,
                when calculating the local mean to use in place of missing value.
            NOTE: if there are (adjacent or otherwise) missing values, then 0
                will be used in their place, when calculating mean.
            """
        if self.bTestForceMissing:
            self.data[5,0] = missing
        lMissing = self.fix_missing_value(missing, 0)
        for iCur in lMissing:
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
            print("INFO:DataSrc:fix_missing_localmean:pos={}:curarea={}:new={}".format(iCur, tData, iMean))
            self.data[tuple(iCur)] = iMean


    def fix_missing(self, fixMissing=None):
        """ fix missing values if required as specified
            fixMissing: None or { "type": <type>, "missing": <missing>, "value": <value> }
                <type>: "value" or "localmean" or "none"
                    if  "value" give <missing> and <value>
                    if "localmean" give <missing>
                    if "none" do nothing
                <missing>: the value in the data to be treated as missing value
                <value>: the value to use in place of missing value
            """
        if fixMissing != None:
            if fixMissing["type"] == "localmean":
                self.fix_missing_localmean(missing=fixMissing["missing"])
            elif fixMissing["type"] == "value":
                self.fix_missing_value(missing=fixMissing["missing"], value=fixMissing["value"])
            elif fixMissing["type"] == "None":
                pass
            else:
                raise NotImplementedError("DataSrc:fix_missing:type:{}".format(fixMissing["type"]))


    def download(self, theUrl = None, localFileName = None):
        """ Download the specified url into specified local file. wget is used for download.

            theUrl: The url to use, if not given same is picked from url instance variable
                in the class instance.
            localFileName: The local file name to store into, if not given same is picked
                from localFileName instance variable in the class instance.
            """
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
        """ The child class needs to implement this function, to setup
            the url to use and the local file name to use, as required
            by it. i.e self.url and self.localFileName.

            One should also specify self.localFileType, which will be used by
            conv_data to decide if any additional processing is required
            after the data is fetched/downloaded.
            """
        raise NotImplementedError("DataSrc: Download data from net...")


    def _set_fetch_date(self, day, month, year):
        """ set the fetch date related instance variables in the current
            class instance (i.e self).
            If date info is not specified, then set it from current time.
            """
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
        """ fetch/download data if not already downloaded/available.
            It calls helper functions to setup the fetch date, as well as
            the url, local file name and file type of fetched data.
            """
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
        """ Child class can add additional logic to help process fetched data by implementing
            this function.
            This is automatically called if xls to csv conversion of datasrc base class is used,
            which occurs after a download, if localFileType is set to "xls".
            Similarly if localFileType is set to "proc", then also this will be called.
            """
        raise NotImplementedError("DataSrc:_fetchconv_postproc: of data fetched and or converted to csv...")


    def conv_data(self):
        """ Automatically called by fetch_data, after data has been fetched.
            It uses the self.localFileType instance variable to decide what to do.
                if "xls", then fetched xls file is converted to csv format.
                    This also triggers the "proc" logic mentioned below.
                if "proc", then _fetchconv_postproc helper is called.
            """
        if self.localFileType == "xls":
            xlsFN = self.localFileName
            (tBase, tExt) = os.path.splitext(xlsFN)
            csvFN = "{}.csv".format(tBase)
            self.conv_xls2csv(xlsFN, csvFN)
            self.localFileName = csvFN
            self.localFileType = "proc"

        if self.localFileType == "proc":
            self._fetchconv_postproc()


    def _prev_day(self, day, month, year):
        """ Return the previous calender date, for a given date.
            """
        for i in range(4):
            day = day - 1
            if (day == 0):
                day = 31
                month = month - 1
                if month == 0:
                    year = year - 1
            try:
                calendar.datetime.date(year, month, day)
                return day, month, year
            except ValueError:
                continue
        raise ValueError("DataSrc:_prev_day:DBG: Couldnt find valid prev day for {}-{}-{}".format(year, month, day))


    def fetch_data(self, day=None, month=None, year=None):
        """ Called by user to fetch data, ideally belonging to the given date.
            If there is no data available for a given date, then it automatically
            tries to fetch data for the previous date (upto 4 prev dates are tried).

            After the data is fetched, it automatically calls conv_data. Which inturn
            may call child class's _fetchconv_postproc, if required.
            """
        for i in range(4):
            try:
                self._fetch_data(day, month, year)
                break
            except ConnectionError:
                day, month, year = self._prev_day(self.fd_day, self.fd_month, self.fd_year)
                print("INFO:DataSrc:fetch_data: Failed fetching data for {}-{}-{}, so trying for {}-{}-{}".format(self.fd_year, self.fd_month, self.fd_day, year, month, day))
        self.conv_data()


    def conv_date_str2int(self, sDate, delimiter="-", iY = 0, iM=1, iD=2, mType="int", bYear2Digit=False):
        """ Helper to convert date in string format to numeric YYYYMMDD
            sDate: the date in string format
            delimiter: the delimiter used to differentiate between date, month and year in string.
            iY, iM, iD: specify the location of year, month and date in the string.
            mType: Check if month is specified as a abbrevation or number in the string.
                "int": 01 - January, ..., 04 April, ..., 12 - December
                anything else: jan - january, apr - april, dec - december.
            bYear2Digit: If true, then year will be in YY format, else YYYY format.
            """
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
        """ A helper function used to extract the header in the specified data file.
            It uses the delimiter and header line info specified to extract the same.
            """
        f = open(fileName)
        i = 0
        for l in f:
            if (i == iHdrLine):
                dprint("DBUG:DataSrc:_load_hdr:type:%s" %(type(l)))
                return l.split(delimiter)
            i += 1
        raise ImportError("DataSrc:_load_hdr: No header found")


    def load_data(self, fileName=None, dtype=float, delimiter=None, skip_header=None, converters=None, iHdrLine=None, usecols=None, fixMissing=None):
        """ load data from specified csv file
            iHdrLine: the column header line among the skip_header lines, starts at 0
            fixMissing: None or as specified by fix_missing function
            """
        if fileName == None:
            fileName = self.localFileName
        print("INFO:DataSrc:Loading:{}".format(fileName))
        self.data = numpy.genfromtxt(fileName, dtype = dtype, delimiter=delimiter, skip_header=skip_header, converters=converters, usecols=usecols)
        self.fix_missing(fixMissing)
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


    def load_data(self, fileName=None, fixMissing=None):
        converters = { 0: lambda x: self.conv_date(x) }
        if fixMissing == None:
            fixMissing = { "type": "value", "missing": numpy.NAN, "value": 0 }
        super().load_data(fileName=fileName, delimiter=",", skip_header=1, converters=converters, iHdrLine=0, fixMissing=fixMissing)
        # Remove the empty last column
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
            sGeoId = sGeoId.decode()
            i = self.geoIds.index(sGeoId)
        except ValueError:
            self.geoIds.append(sGeoId)
            i = len(self.geoIds) - 1
        return i


    def _fetchconv_postproc(self):
        """ dumb, but simple for now
            """
        fIn = open(self.localFileName)
        fOutName = "{}.tmp".format(self.localFileName)
        fOut = open(fOutName, "w+")
        for l in fIn:
            if l.find('"') == -1:
                fOut.write(l)
                continue
            fOut.write(replace_ifwithin(l, '"', ',', '_'))
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
        super().load_data(fileName=self.localFileName, dtype=int, delimiter=",", skip_header=1, converters=converters, iHdrLine=0, usecols=cols)
        minDate = self.data[:,0].min()
        maxDate = self.data[:,0].max()
        numRows = maxDate-minDate+1
        numRows = len(numpy.unique(self.data[:,0]))
        numCols = self.data[:,2].max()+1+2
        #data = numpy.ones((numRows, numCols)) * numpy.nan
        data = numpy.zeros((numRows, numCols))
        iDate = 0
        for date in numpy.arange(minDate, maxDate+1):
            dateData = self.data[self.data[:,0] == date]
            for cur in dateData:
                data[iDate,0] = date
                data[iDate,cur[2]+2] = cur[1]
            if len(dateData) >= 1:
                iDate += 1
        print(minDate, maxDate)
        self.olddata = self.data
        self.hdr = [ "date", "Total2Calc" ] + self.geoIds
        self.data = data
        # Save to csv file
        fOutName = "{}.tmp2".format(self.localFileName)
        sHdr = ""
        for sCol in self.hdr:
            sHdr += "{},".format(sCol)
        sHdr = sHdr.rstrip(',')
        numpy.savetxt(fOutName, self.data, delimiter=",", header=sHdr, comments="", fmt="%d")
        os.rename(fOutName, self.localFileName)


    def conv_date(self, sDate):
        iDate = self.conv_date_str2int(sDate, delimiter="/", iY=2, iD=1, iM=0, mType="int", bYear2Digit=False)
        fDate = float(iDate)
        #print(sDate, fDate)
        return iDate


    def load_data(self, fileName=None, fixMissing=None):
        if fixMissing == None:
            fixMissing = { "type": "value", "missing": numpy.NAN, "value": 0 }
        super().load_data(fileName=fileName, delimiter=",", skip_header=1, iHdrLine=0, fixMissing=fixMissing)
        dprint("DBUG:DataSrc:EU:load_data:hdr-type:%s" %(type(self.hdr[-2])))



if __name__ == "__main__":

    import matplotlib.pyplot as plt

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
        #theDataSrc.fix_missing_localmean()
        plt.subplot(2,1,1)
        plt.plot(theDataSrc.data[:,2:])
        plt.yscale("log")
        plt.subplot(2,1,2)
        plt.boxplot(theDataSrc.data[:,2:])
        plt.show()



# vim: set softtabstop=4 expandtab shiftwidth=4: #
