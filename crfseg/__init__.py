#!/usr/bin/env
# -*- encoding: utf-8 -*-

from __future__ import with_statement
import sys, errno
import os, re
import codecs
import logging
import CRFPP


def get_sentence_seg():
    cutlist = " .[。，,！……!《》<>\"':：？\?、\|“”‘’；]{}（）{}【】()｛｝（）：？！。，;、~——+％%`:“”＂'‘\n\r"
    if not isinstance(cutlist, unicode):
        try:
            cutlist = cutlist.decode('utf-8')
        except UnicodeDecodeError:
            cutlist = cutlist.decode('gbk','ignore')
    sent_seg = frozenset(cutlist)
    return sent_seg

def create_model(filename=None):
    if not filename:
        the_file = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(the_file,'data','crf_seg.model')
    crf_model =  CRFPP.Model("-m %s -v 3" % filename)
    return crf_model

# Share single CRF++ model
crf_model_global = create_model()
sent_seg_global = get_sentence_seg()
ascii_global = re.compile('(\d+)|([a-zA-Z]+)', re.I|re.U)

def create_tagger():
    return crf_model_global.createTagger()

def seg_regex(sentence):
    start = 0
    for m in ascii_global.finditer(sentence):
        yield (sentence[start:m.start(0)], True)
        yield (sentence[m.start(0):m.end(0)], False)
        start = m.end(0)
    yield (sentence[start:], True)

def cut_to_tagger(line):
    if not isinstance(line, unicode):
        try:
            line = line.decode('utf-8')
        except UnicodeDecodeError:
            line = line.decode('gbk','ignore')
    for s,need_cut in seg_regex(line):
        if need_cut:
            if s != '':
                str = ''
                for c in s:
                    if c in sent_seg_global:
                        if str != '':
                            for cn in str:
                                yield cn+'\tCN'
                        str = ''
                        yield c+'\tPUNC'
                    else:
                        str += c
                if str != '':
                    for cn in str:
                        yield cn+'\tCN'
        else:
            yield s+'\tASCII'

def tagger_cut(line, tagger):
    tagger.clear()
    for s in cut_to_tagger(line):
        #print s
        tagger.add(s.encode('utf-8'))
    tagger.add('.\tPUNC')
    tagger.parse()

    size = tagger.size()
    xsize = tagger.xsize()
    str = ''
    for i in range(0, (size - 1)):
       c = tagger.x(i,0).decode('utf-8')
       tag = tagger.y2(i) 
       #print 'test ', c,tag
       if tag == 'B':
           str = c
       elif tag == 'B1' or tag == 'B2':
            str += c
       elif tag == 'E':
            yield str+c
            str = ''
       else:
            yield c
            str = ''

# Quick cut but slow in too many loop
def cut(line):
    tagger = crf_model_global.createTagger()
    for s in  tagger_cut(line, tagger):
        yield s

#for s in cut(u'海运业雄踞全球之首 ，按吨位计占世界总数的１７％ 。'):
#    print s,'/',
#print '\n'
