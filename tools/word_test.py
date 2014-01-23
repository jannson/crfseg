#!/usr/bin/env
# -*- encoding: utf-8 -*-

import re
import os
import codecs
import cppjiebapy
import zerorpc
from crfseg import Tagger

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
    #for t in s.cut_pos(u'你们这些人啊'):
    #    print t
    #return
    with codecs.open(filename,'r','utf-8') as file:
        out = codecs.open("./crf", 'w', 'utf-8')
        for line2 in file:
            line = line2.replace('\r','')
            cs = [c.decode('utf-8') for c in s.cut_pos(line.encode('utf-8'))]
            out.write(' '.join(cs))

def test4():
    corpus = [u'SCANV网址安全中心(http://scanv.com)是一个综合性的网址安全服务平台。通过网址安全中心，用户可以方便的查询到要访问的网址是否存在恶意行为，同时可以在SCANV中在线举报曝光违法恶意网站。',
            u'工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作',]

    tagger = Tagger()
    for str in corpus:
        print '\nCPPJIEBA:'
        for s in tagger.pos(list(cppjiebapy.cut(str))):
            print s[0],'/',s[1], " ",

        print '\nCRF:'
        for s in tagger.cut_pos(str):
            print s[0],'/',s[1], " ",
        print '\n'
def test5():
    trans = zerorpc.Client("tcp://0.0.0.0:3333", timeout=10000)
    s = u'飛起來'
    s = trans.trad2simp(s.encode('utf-8'))
    print s
#test1()
#test2()
#test3()
#test4()
test5()

