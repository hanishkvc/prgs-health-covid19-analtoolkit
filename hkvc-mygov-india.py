#!/usr/bin/env python3

import sys
import os
import subprocess
import time
import xml.etree.ElementTree as ET


def get_data(ts):
    tFile = "{}.html".format(ts)
    if os.path.exists(tFile):
        print("WARN:get_data:{} already exists".format(tFile))
        return tFile
    tCmd = [ "wget", "https://www.mygov.in/corona-data/covid19-statewise-status", "--output-document={}"]
    tCmd[2] = tCmd[2].format(tFile)
    print(tCmd)
    subprocess.call(tCmd)
    return tFile


class MyParser:
    depth = 0
    maxDepth = 0
    def start(self, tag, attrib):
        self.depth += 1
        if (self.maxDepth < self.depth):
            self.maxDepth = self.depth
        print(tag, attrib)

    def end(self, tag):
        self.depth -= 1

    def data(self, data):
        pass

    def close(self):
        return self.maxDepth


def extract_data_default(tFile):
    tree = ET.parse(tFile)
    tree.dump()
    root = tree.getroot()
    for child in root:
        print("{}, {}".format(child.tag, child.attrib))


def extract_data(tFile):
    myParser = MyParser()
    myParser = ET.XMLParser(target=myParser)
    tData = open(tFile)
    tData = tData.read()
    myParser.feed(tData)
    myParser.close()

ts = time.gmtime()
ts = "{:04}{:02}{:02}GMT{:02}".format(ts.tm_year, ts.tm_mon, ts.tm_mday, ts.tm_hour)
theFile=get_data(ts)
extract_data(theFile)

