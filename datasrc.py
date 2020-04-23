#
# DataSrc Base Class
# v20200423IST1944, HanishKVC
#

import time
import subprocess

class DataSrc:

    def download(self, theUrl, dstFileName):
        print("INFO:DataSrc:{}:downloading...".format(theUrl))
        tCmd = [ "wget", theUrl, "--output-document={}"]
        tCmd[2] = tCmd[2].format(dstFileName)
        subprocess.call(tCmd)

    def fix_url_filename(self, url, fileName):
        raise NotImplementedError("DataSrc: Download data from net...")

    def _set_fetch_date(self, day, month, year):
        curTime = time.gmtime()
        if day = None:
            self.fd_day = curTime.tm_mday
        else:
            self.fd_day = day
        if month = None:
            self.fd_month = curTime.tm_mon
        else:
            self.fd_month = month
        if year = None:
            self.fd_year = curTime.tm_year
        else:
            self.fd_year = year

    def fetch_data(self, url, fileName, day=None, month=None, year=None):
        _set_fetch_date(day, month, year)
        url, fileName = fix_url_filename(url, fileName)
        dstFileName = "data/{}-{}".format(self.name, fileName)
        if os.path.exists(dstFileName) and (os.path.getsize(dstFileName)>128):
            print("INFO:{}:already downloaded".format(dstFileName))
            return True
        download(url, dstFileName)

    
        



# vim: set softtabstop=4 expandtab: #
