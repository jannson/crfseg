#!/usr/bin/env
# -*- encoding: utf-8 -*-

from __future__ import with_statement
import sys, errno
import os, re
import codecs
import logging
import CRFPP
#from trie import Trie

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

def create_syno_trie():
    the_file = os.path.dirname(os.path.abspath(__file__))
    syno_file = os.path.join(the_file,'data','synosynm.txt')
    #trie = Trie()
    dict = {}
    with codecs.open(syno_file, 'r', 'utf-8') as file:
        all_lines = file.read().split(u'\n')
        for line in sorted(all_lines, key=lambda x:len(x), reverse=True):
            words = []
            for word in line.split():
                w1,w2 = word.split(',')
                words.append((w1.strip(), w2.strip()))
            for word in words:
                if not word in dict:
                    dict[word] = words[0]
    #for k,v in dict.iteritems():
    #    trie[k] = v
    #return trie
    return dict

def syno_word(trie, w):
    v = w
    while True:
        if w in trie and trie[w] != v:
            v = trie[w]
            w = v
        else:
            break
    return v

# Share single CRF++ model
(seg_model_global, pos_model_global) = create_model()
sent_seg_global = get_sentence_seg()
stop_words_global = get_stop_words()
syno_trie_global = create_syno_trie()
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

    def cut_syno(self, txt):
        toks = self.cut_pos(txt)
        for t in toks:
            if t[1] != 'w':
                yield syno_word(syno_trie_global, t)[0]
            else:
                yield t[0]

    def normal_words(self, words):
        for t in self.pos(words):
            #print t[0], t[1]
            if t[1] == 'u' or t[1] == 'y':
                continue
            elif t[1] == 'd' and t[0].find(u'不') < 0 and t[0].find(u'没') < 0:
                continue
            elif t[1] != 'w':
                yield syno_word(syno_trie_global, t)[0]
            else:
                yield t[0]

    def cut_filter(self, txt, stopwords=stop_words_global):
        for x in self.cut(txt):
            if x not in stop_words_global:
                yield x

if __name__ == '__main__':
    tagger = Tagger()
    stest = u'您们都跑哪里去玩了？最前面的那个地方 *  是什么！您是谁，您想怎样? 高兴不！不错，我就是非常爱你！你这个人怎么这么讨厌。我怎么这么不爱你啊'
    print stest
    #print u' '.join(list(tagger.cut_syno(stest)))
    print u' '.join(list(tagger.normal_words(tagger.cut(stest))))
    print '\n'
