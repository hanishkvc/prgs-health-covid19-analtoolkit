#!/usr/bin/env python3
# Covid19 Data extractor from mygov.in html page
# v20200415IST1850, HanishKVC
#

import sys
import os
import subprocess
import time
import xml.etree.ElementTree as ET
import xmlparser as xp


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


class MyParser_ETXMLParser:
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


def extract_data_ETdefault(tFile):
    tree = ET.parse(tFile)
    tree.dump()
    root = tree.getroot()
    for child in root:
        print("{}, {}".format(child.tag, child.attrib))


def extract_data_ETMyParser(tFile):
    myParser = MyParser_ETXMLParser()
    myParser = ET.XMLParser(target=myParser)
    tData = open(tFile)
    tData = tData.read()
    myParser.feed(tData)
    myParser.close()


class MyParserHandler:

    smMode = ""
    dData = {}
    sState = None
    iConfirmed = None
    iCured = None
    def error(self, sLine, sErrorType):
        print("ERROR:{}:{}".format(sErrorType, sLine))

    def tag_start(self, sTag, dAttribs, iTagLvl, sRawTag, sLine):
        print(sTag, dAttribs)
        if (sTag.lower() == "div"):
            if "class" in dAttribs:
                if dAttribs["class"].find("field-item even") != -1:
                    if self.smMode == "state":
                        self.smMode = "state-data"
                    if self.smMode == "confirmed":
                        self.smMode = "confirmed-data"
                    if self.smMode == "cured":
                        self.smMode = "cured-data"
                    if self.smMode == "deaths":
                        self.smMode = "deaths-data"
                if dAttribs["class"].find("field-select-state") != -1:
                    self.smMode = "state"
                if dAttribs["class"].find("field-total-confirmed") != -1:
                    self.smMode = "confirmed"
                if dAttribs["class"].find("field-cured") != -1:
                    self.smMode = "cured"
                if dAttribs["class"].find("field-deaths") != -1:
                    self.smMode = "deaths"

    def tag_end(self, sTag, dAttribs, iTagLvl, sData, sRawTag, sLine):
        print(sData)
        if self.smMode == "state-data":
            if (self.sState != None) and (self.iConfirmed != None):
                self.dData[self.sState] = [self.iConfirmed, self.iCured, self.iDeaths]
                self.iConfirmed = None
                self.iCured = None
                self.iDeaths = None
            self.sState = sData.strip()
            self.smMode = ""
        if self.smMode == "confirmed-data":
            self.iConfirmed = float(sData.strip())
            self.smMode = ""
        if self.smMode == "cured-data":
            self.iCured = float(sData.strip())
            self.smMode = ""
        if self.smMode == "deaths-data":
            self.iDeaths = float(sData.strip())
            self.smMode = ""


def extract_data(tFile):
    myParser = xp.XMLParser()
    myHandler = MyParserHandler()
    myParser.open(tFile)
    myParser.parse(myHandler)
    print(myHandler.dData)


if len(sys.argv) == 1:
    ts = time.gmtime()
    ts = "{:04}{:02}{:02}GMT{:02}".format(ts.tm_year, ts.tm_mon, ts.tm_mday, ts.tm_hour)
    theFile=get_data(ts)
else:
    theFile = sys.argv[1]
extract_data(theFile)
