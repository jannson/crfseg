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
        return [s.encode('utf-8') for s in Tagger.cut(line)]

s = zerorpc.Server(CrfServer())
s.bind("tcp://0.0.0.0:3333")
s.run()

