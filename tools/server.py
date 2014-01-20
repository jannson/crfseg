#!/usr/bin/env
# -*- encoding: utf-8 -*-

import zerorpc
import logging
from gevent import monkey; monkey.patch_all() 
from crfseg import Tagger

logging.basicConfig()

class CrfServer(object):
    tagger = Tagger()
    def cut(self, line):
        return [s.encode('utf-8') for s in self.tagger.cut(line)]
    def cut_pos(self, line):
        return [(s[0]+'/'+s[1]).encode('utf-8') for s in self.tagger.cut_pos(line)]

s = zerorpc.Server(CrfServer())
s.bind("tcp://0.0.0.0:3333")
s.run()

