#!/usr/bin/env
# -*- encoding: utf-8 -*-

from __future__ import with_statement
import sys, errno
import os
import codecs
from optparse import OptionParser
import logging
import CRFPP


#tagger = CRFPP.Tagger("-m /opt/bamboo/index/crf_seg.model -v 3 -n2")
#tagger = CRFPP.Tagger("-m ./6.model -v 3 -n2")
model = CRFPP.Model("-m /opt/bamboo/index/crf_seg.model -v 3 -n2")
tagger = model.createTagger()

# clear internal context
tagger.clear()

str = u"年我们是中国人"
tagger.add((u"199855\tASCII \tB").encode('utf-8'))
for t in str:
    tagger.add((t+ "\tCN \tB").encode('utf-8'))

print "column size: " , tagger.xsize()
print "token size: " , tagger.size()
print "tag size: " , tagger.ysize()

# parse and change internal stated as 'parsed'
tagger.parse()

print "tagset information:"
ysize = tagger.ysize()
for i in range(0, ysize-1):
    print "tag " , i , " " , tagger.yname(i)

print "conditional prob=" , tagger.prob(), " log(Z)=" , tagger.Z()

size = tagger.size()
xsize = tagger.xsize()
print 'the size ', size, " ", xsize
for i in range(0, (size - 1)):
   for j in range(0, (xsize-1)):
      print tagger.x(i, j) , "\t",
   print tagger.y2(i) , "\t",
   #print "Details",
   #for j in range(0, (ysize-1)):
   #   print "\t" , tagger.yname(j) , "/prob=" , tagger.prob(i,j),"/alpha=" , tagger.alpha(i, j),"/beta=" , tagger.beta(i, j),
   print "\n",

print "nbest outputs:"
for n in range(0, 2):
    if (not tagger.next()):
        continue
    print "nbest n=" , n , "\tconditional prob=" , tagger.prob()
    # you can access any information using tagger.y()...

print "Done"
