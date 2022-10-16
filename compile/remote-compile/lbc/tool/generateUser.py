# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     generateUser
   Description :
   Author :       liaozhaoyan
   date：          2021/7/17
-------------------------------------------------
   Change Activity:
                   2021/7/17:
-------------------------------------------------
"""
__author__ = 'liaozhaoyan'

import re
import os
import sys
import json
import shlex
from subprocess import PIPE, Popen
from checkSymbol import ClbcSymbol
# from parseArgs import CpaserGdbArgs
from parsePahole import CparsePahole
import hashlib


class CgenerateUser(object):
    def __init__(self, path='./'):
        self.__path = path
        self._skel = os.path.join(self.__path, '.output/lbc.skel.h')
        self._bpfc = os.path.join(self.__path, "bpf/lbc.bpf.c")
        self._bpfo = os.path.join(self.__path, '.output/lbc.bpf.o')
        self._reMaps = re.compile("struct bpf_map \\*[A-Za-z0-9_]+;")

    def upSkel(self, skel):
        self._skel = skel

    def getSkelMaps(self):
        rs = []
        with open(self._skel) as fSkel:
            line = fSkel.read()
            maps = self._reMaps.findall(line)
            for m in maps:
                t, v = m.rsplit("*", 1)
                rs.append(v[:-1])
        return rs

    def createUser(self, ver, arch, env="", oFile='src/bpf_init.c'):

        s = self.genModelSymbols(ver, arch, env)
        if not os.path.exists("src"):
            os.mkdir("src")
        with open(os.path.join(self.__path, oFile), 'w') as f:
            f.write(s)

    def genModelSymbols(self, ver, arch, env=""):
        a = CparsePahole(self._bpfo)
        dOut = {}
        dMaps = {}
        with open(self._bpfc, 'r') as f:
            sym = ClbcSymbol()
            s = f.read()
            s += env
            dOut['hash'] = hashlib.sha256(s).hexdigest()
            ds = sym.findEvent(s)
            for k, v in ds.items():
                dMaps[k] ={ 'type': v['type'], 'ktype': None, "vtype": a.parseType(v['vtype'])}
            hs = sym.findMaps(s)
            for k, v in hs.items():
                dMaps[k] = {'type': v['type'], 'ktype': a.parseType(v['ktype']), "vtype": a.parseType(v['vtype'])}
        dOut['maps'] = dMaps
        dOut['arch'] = arch
        dOut['kern_version'] = ver
        print(dOut['kern_version'])
        s = json.dumps(dOut).replace('"', '\\"')
        return """

#include "lbc_static.h"

        
const char* lbc_get_map_types(void)
{
    const char* s = "%s";
    return s;
}  
     
        """ % (s)


if __name__ == "__main__":
    g = CgenerateUser()
    if len(sys.argv) <= 3:
        g.createUser(sys.argv[1], sys.argv[2])
    else:
        g.createUser(sys.argv[1], sys.argv[2], sys.argv[3])
