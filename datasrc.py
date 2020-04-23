#
# DataSrc Base Class
# v20200423IST1944, HanishKVC
#

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
        _set_fetch_date(day, month, year)
        _fix_url_filenames()
        if os.path.exists(self.dstFileName) and (os.path.getsize(self.dstFileName)>128):
            print("INFO:DataSrc:{}:already downloaded".format(self.dstFileName))
            return True
        download()



class Cov19InDataSrc(DataSrc):

    #urlFmt = "http://api.covid19india.org/states_daily_csv/confirmed.csv"
    fileNameFmt = "confirmed.csv"
    urlFmt = "http://api.covid19india.org/states_daily_csv/{}"
    dstFileNameFmt = "data/{}-{}{}{}-{}"

    def _init_(self):
        self.name = "Cov19In"


    def _fix_url_filenames(self):
        self.fileName = fileNameFmt
        self.url = urlFmt.format(self.fileName)
        self.dstFileName = dstFileNameFmt.format(self.name, self.fd_year, self.fd_month, self.fd_day, self.fileName)



if __name__ == "__main__":
    theDataSrc = Cov19InDataSrc()
    theDataSrc.fetch_data()



# vim: set softtabstop=4 expandtab: #
