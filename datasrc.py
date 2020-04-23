#
# DataSrc Base Class
# v20200423IST1944, HanishKVC
#

import time

class DataSrc:

    def download(self):
        raise NotImplementedError("DataSrc: Download data from net...")

    def fetch_data(self, url, fileName, day=None, month=None, year=None):
        if os.path.exists(fileName) and (os.path.getsize(fileName)>128):
            print("INFO:{}:already downloaded".format(tFile))
            return True
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
        download(url, fileName)

    
        





# vim: set softtabstop=4 expandtab: #
