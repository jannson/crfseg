#!/usr/bin/env
# -*- coding: UTF-8 -*-

import sys, os, os.path, codecs, math
import logging
import unittest
import tempfile
import logging
import itertools

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.externals import joblib
import crfseg

#TODO for sentiment

def train(neg=None, pos=None):
    the_file = os.path.dirname(os.path.abspath(__file__))
    if not neg:
        neg = os.path.join(the_file, '..', 'origin', 'neg.txt')
    if not pos:
        pos = os.path.join(the_file, '..', 'origin', 'pos.txt')
    
    tagger = crfseg.create_tagger()
    tok_cn = lambda (x): crfseg.cut_zh(x, tagger)
    
    tfidf = TfidfVectorizer(tokenizer=tok_cn, sublinear_tf=True, max_df=0.5)
    pipe = Pipeline([
        ('tfidf', tfidf),
    #    ('svd', TruncatedSVD(32)),
    #    ('normal', Normalizer(copy=False))
        ])
    '''
    hasher = HashingVectorizer(n_features=2**16,
                               tokenizer=tok_cn, non_negative=True,
                               norm=None, binary=False)
    '''

    #clf = SGDClassifier(loss='log', penalty='l2', alpha=0.00001, n_iter=50, fit_intercept=True)
    #clf = MultinomialNB()
    clf = BernoulliNB()
    
    neg_file = codecs.open(neg, 'r', 'utf-8')
    pos_file = codecs.open(pos, 'r', 'utf-8')

    x_train = []
    y_train = []
    
    i = 0
    for line in neg_file:
        x_train.append(line)
        y_train.append(0)
    for line in pos_file:
        x_train.append(line)
        y_train.append(1)
    
    print 'begin transform'
    #x_train = hasher.transform(x_train)
    x_train = pipe.fit_transform(x_train)
    print 'begin fit'
    clf.fit(x_train, y_train)

    print 'begin save'
    tfidf_file = os.path.join(the_file, 'data', 'tfidf.pkl')
    clf_file = os.path.join(the_file, 'data', 'sgdc_clf.pkl')
    #_ = joblib.dump(tfidf, tfidf_file, compress=9)
    _ = joblib.dump(clf, clf_file, compress=9)

    print 'begin test'
    x_test = [u'这个东西真心很赞']
    #x_test = hasher.transform(x_test)
    x_test = pipe.transform(x_test)
    print clf.predict(x_test)

try:
    clf_global = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__))
        , 'data', 'sgdc_clf.pkl'))
except:
    clf_global = None

def predict(line, tagger):
    tok_cn = lambda (x): crfseg.cut_zh(x, tagger)

    hasher = HashingVectorizer(n_features=2**16,
                               tokenizer=tok_cn, non_negative=True,
                               norm=None, binary=False)
    x_test = hasher.transform([line])
    return clf_global.predict_proba(x_test)

train()
#tagger = crfseg.create_tagger()
#print predict(u'这个东西真心很赞', tagger)
