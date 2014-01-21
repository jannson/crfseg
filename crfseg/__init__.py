#!/usr/bin/env
# -*- encoding: utf-8 -*-

from __future__ import with_statement
import sys, errno
import os, re
import codecs
import logging
import CRFPP


def get_sentence_seg():
    cutlist = u" .[。，,！……*!《》<>\"':：？\?、\|“”‘’；]{}（）{}【】()｛｝（）：？！。，;、~——+％%`:“”＂'‘\n\r"
    sent_seg = frozenset(cutlist)
    return sent_seg

def get_stop_words():
    the_file = os.path.dirname(os.path.abspath(__file__))
    sent_seg = get_sentence_seg()
    f = codecs.open(os.path.join(the_file, 'data', 'stopwords.txt'))
    words = f.read().split('\n')
    words += list(sent_seg)
    return frozenset(words)

def create_model(seg_file=None, pos_file=None):
    the_file = os.path.dirname(os.path.abspath(__file__))
    if not seg_file:
        seg_file = os.path.join(the_file,'data','crf_seg.model')
    if not pos_file:
        pos_file = os.path.join(the_file,'data','crf_pos.model')
    seg_model = CRFPP.Model("-m %s" % seg_file)
    pos_model = CRFPP.Model("-m %s" % pos_file)
    return (seg_model, pos_model)

# Share single CRF++ model
(seg_model_global, pos_model_global) = create_model()
sent_seg_global = get_sentence_seg()
stop_words_global = get_stop_words()
ascii_global = re.compile('(\d+)|([a-zA-Z]+)', re.I|re.U)
space_global = re.compile('[\s\t\r\n]+', re.I|re.U)

#TODO move to utils.py
def to_unicode(txt):
    if not isinstance(txt, unicode):
        try:
            txt = txt.decode('utf-8')
        except UnicodeDecodeError:
            txt = txt.decode('gbk','ignore')
    return txt

def seg_regex(sentence):
    start = 0
    for m in ascii_global.finditer(sentence):
        yield (sentence[start:m.start(0)], True)
        yield (sentence[m.start(0):m.end(0)], False)
        start = m.end(0)
    yield (sentence[start:], True)

def space_regex(sentence):
    start = 0
    for m in space_global.finditer(sentence):
        yield (sentence[start:m.start(0)], True)
        yield (sentence[m.start(0):m.end(0)], False)
        start = m.end(0)
    yield (sentence[start:], True)

class Tagger(object):
    def __init__(self):
        self.seg_ = seg_model_global.createTagger()
        self.pos_ = pos_model_global.createTagger()

    def seg(self, txt):
        txt = to_unicode(txt)
        for s,need_cut in seg_regex(txt):
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

    def cut2(self, txt):
        tagger = self.seg_
        tagger.clear()
        for s in self.seg(txt):
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

    def cut(self, txt):
        for s,need_cut in space_regex(txt):
            if need_cut:
                #print s, ' NEED'
                if s != "":
                    for c in self.cut2(s):
                        yield c
            else:
                yield s
    
    def pos(self, toks):
        tagger = self.pos_
        tagger.clear()
        for tok in toks:
            tagger.add(tok.encode('utf-8'))
        tagger.add(".")
        tagger.parse()
        size = tagger.size()
        xsize = tagger.xsize()
        for i in range(0, (size - 1)):
           c = tagger.x(i,0).decode('utf-8')
           tag = tagger.y2(i) 
           yield (c, tag)

    def cut_pos(self, txt):
        toks = self.cut(txt)
        return self.pos(toks)

    def cut_filter(self, txt, stopwords=stop_words_global):
        for x in self.cut(txt):
            if x not in stop_words_global:
                yield x

#tagger = Tagger()
#for s in tagger.cut_filter(u'海运业雄踞全球之首 ，按吨位计占世界总数的１７％ 。'):
#    print s,
#print '\n'
