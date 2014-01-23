#!/usr/bin/env
# -*- encoding: utf-8 -*-

import zerorpc
import logging
from gevent import monkey; monkey.patch_all() 
from crfseg import Tagger
from crfseg.opencc import OpenCC, DictType

logging.basicConfig()

path1 = ['simp_to_trad_characters.ocd', 'simp_to_trad_phrases.ocd']
path2 = ['trad_to_simp_characters.ocd', 'trad_to_simp_phrases.ocd']

class CrfServer(object):
    tagger = Tagger()
    def cut(self, line):
        return [s.encode('utf-8') for s in self.tagger.cut(line)]
    def cut_pos(self, line):
        return [(s[0]+'/'+s[1]).encode('utf-8') for s in self.tagger.cut_pos(line)]

def trad():
    with OpenCC() as cc:
        for p in path2:
            cc.dict_load(p, DictType.DATRIE)
        class Trans(object):
            def trad2simp(self, s):
                return cc.convert(s)

        tran = zerorpc.Server(Trans())
        tran.bind("tcp://0.0.0.0:3333")
        tran.run()

trad()

