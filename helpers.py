#!/usr/bin/env python3
# A set of helpers
# v20200430IST1725, HanishKVC
#

GLOBAL_DBGLEVEL=10
def dprint(sMsg, dbgLvl=GLOBAL_DBGLEVEL):
    """ dprint the given msg if its dbgLvl is
        less than the current global_dbglvl
        """
    if dbgLvl < GLOBAL_DBGLEVEL:
        print(sMsg)



def replace_ifwithin(lIn, withIn='"', find=',', replace='_'):
    bWithIn = False
    lOut = ""
    for c in lIn:
        if c == withIn:
            bWithIn = not bWithIn
        if bWithIn and (c == find):
            c = replace
        lOut += c
    return lOut



# vim: set softtabstop=4 expandtab shiftwidth=4: #
