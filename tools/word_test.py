#!/usr/bin/env
# -*- encoding: utf-8 -*-

import re
import os
import codecs
import cppjiebapy
import crfseg
import zerorpc

filename = '/opt/projects/svn_source/people/icwb2-data/testing/msr_test.utf8'

def test1():
    with codecs.open(filename,'r','utf-8') as file:
        out = codecs.open("./jieba", 'w', 'utf-8')
        for line in file:
            out.write(' '.join(list(cppjiebapy.cut(line))))

def test2():
    with codecs.open(filename,'r','utf-8') as file:
        out = codecs.open("./crf", 'w', 'utf-8')

        #out.write(' '.join(list(crfseg.cut(file.read()))))
        
        tagger = crfseg.create_tagger()
        for line in file:
            out.write(' '.join(list(crfseg.tagger_cut(line, tagger))))

def test3():
    s = zerorpc.Client("tcp://0.0.0.0:3333", timeout=10000)
    #for t in s.cut(u'你们这些人啊'):
    #    print t
    with codecs.open(filename,'r','utf-8') as file:
        out = codecs.open("./crf", 'w', 'utf-8')
        for line2 in file:
            line = line2.replace('\r','')
            cs = [c.decode('utf-8') for c in s.cut(line.encode('utf-8'))]
            out.write(' '.join(cs))

#test1()
#test2()
test3()
