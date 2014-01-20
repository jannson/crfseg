#!/usr/bin/env
# -*- encoding: utf-8 -*-

import crfseg
import zerorpc
import logging
from gevent import monkey; monkey.patch_all() 

logging.basicConfig()

class CrfServer(object):
    global_tagger = crfseg.create_tagger()
    def cut(self, line):
        return [s.encode('utf-8') for s in crfseg.tagger_cut(line, self.global_tagger)]

s = zerorpc.Server(CrfServer())
s.bind("tcp://0.0.0.0:3333")
s.run()

