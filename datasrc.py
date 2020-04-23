#
# DataSrc Base Class plus additional Classes
# v20200423IST2313, HanishKVC
#

import os
import time
import subprocess

class DataSrc:

    def download(self, theUrl = None, dstFileName = None):
        if theUrl == None:
            theUrl = self.url
        if dstFileName == None:
            dstFileName = self.dstFileName
        print("INFO:DataSrc:{}:downloading...".format(theUrl))
        tCmd = [ "wget", theUrl, "--output-document={}"]
        tCmd[2] = tCmd[2].format(dstFileName)
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
        if os.path.exists(self.dstFileName) and (os.path.getsize(self.dstFileName)>128):
            print("INFO:DataSrc:{}:already downloaded".format(self.dstFileName))
            return True
        self.download()



class Cov19InDataSrc(DataSrc):

    #urlFmt = "http://api.covid19india.org/states_daily_csv/confirmed.csv"
    fileNameFmt = "confirmed.csv"
    urlFmt = "http://api.covid19india.org/states_daily_csv/{}"
    dstFileNameFmt = "data/{}-{}{:02}{:02}-{}"

    def __init__(self):
        self.name = "Cov19In"


    def _fix_url_filenames(self):
        self.fileName = self.fileNameFmt
        self.url = self.urlFmt.format(self.fileName)
        self.dstFileName = self.dstFileNameFmt.format(self.name, self.fd_year, self.fd_month, self.fd_day, self.fileName)



if __name__ == "__main__":
    theDataSrc = Cov19InDataSrc()
    theDataSrc.fetch_data()



# vim: set softtabstop=4 expandtab: #
