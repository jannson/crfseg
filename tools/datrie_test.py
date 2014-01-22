#!/usr/bin/env
# -*- encoding: utf-8 -*-

import datrie

t2 = datrie.Trie(ranges=[(u'\u4e00', u'\u9fff')])
w1 = u'地位'
w2 = u'的地位'
w3 = u'极高的地位'
w4 = u'极高'
w5 = u'的'

t2[w2] = 1
t2[w4] = 2
t2[w5] = 3
print 'w1 %s in t2 is ' % w1, w1 in t2
print 'w3 %s in t2 is ' % w3, w3 in t2
assert not w1 in t2
assert  w2 in t2
assert not w3 in t2
print t2.items()
