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

    def download(self, theUrl = None, localFileName = None):
        if theUrl == None:
            theUrl = self.url
        if localFileName == None:
            localFileName = self.localFileName
        print("INFO:DataSrc:{}:downloading...".format(theUrl))
        tCmd = [ "wget", theUrl, "--output-document={}"]
        tCmd[2] = tCmd[2].format(localFileName)
        subprocess.call(tCmd)


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


    def fetch_data(self, day=None, month=None, year=None):
        self._set_fetch_date(day, month, year)
        self._fix_url_filenames()
        if os.path.exists(self.localFileName) and (os.path.getsize(self.localFileName)>128):
            print("INFO:DataSrc:{}:already downloaded".format(self.localFileName))
            return True
        self.download()


    def conv_data(self):
        raise NotImplementedError("DataSrc: Conv data to csv...")


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


    def load_data(self, fileName=None, delimiter=None, skip_header=None, converters=None, iHdrLine=None):
        """
            iHdrLine: the column header line among the skip_header lines, starts at 0
            """
        if fileName == None:
            fileName = self.localFileName
        print("INFO:DataSrc:Loading:{}".format(fileName))
        if skip_header != None:
            f = open(fileName)
            i = 0
            for l in f:
                if i >= skip_header:
                    break
                if (iHdrLine != None) and (i == iHdrLine):
                    self.hdr = l.split(delimiter)
                i += 1
        self.data = numpy.genfromtxt(fileName, delimiter=delimiter, skip_header=skip_header, converters=converters)



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


    def conv_date(self, sDate):
        return float(self.conv_date_str2int(sDate, iY=2, iD=0, mType="abbr", bYear2Digit=True))


    def load_data(self, fileName=None):
        converters = { 0: lambda x: self.conv_date(x) }
        super().load_data(fileName=fileName, delimiter=",", skip_header=1, converters=converters, iHdrLine=0)
        self.hdr = self.hdr[:-1]
        self.data = self.data[:,:-1]



if __name__ == "__main__":
    theDataSrc = Cov19InDataSrc()
    fileName = None
    if len(sys.argv) == 1:
        theDataSrc.fetch_data()
    else:
        fileName = sys.argv[1]
    theDataSrc.load_data(fileName)
    print(theDataSrc.hdr)
    print(theDataSrc.data)



# vim: set softtabstop=4 expandtab: #
