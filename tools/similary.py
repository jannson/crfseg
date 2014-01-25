#!/usr/bin/env
# -*- encoding: utf-8 -*-

# import modules and set up logging
import os,sys,codecs,re
from gensim.models import word2vec
from crfseg import Tagger
import logging
from multiprocessing import Pool

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.INFO)

en_word_re = re.compile(ur'[\u4e00-\u9fa5]+', re.I|re.U)

def get_sents():
    the_file = os.path.dirname(os.path.abspath(__file__))
    the_file = os.path.join(the_file, '..', 'origin', 'people-daily-bamboo-edition.txt')

    i = 0
    sens = []
    with codecs.open(the_file, 'r', 'utf-8') as file:
        for line in file:
            line = line.replace('\r','').replace('\n','')
            lis = line.split(u'。')
            li = []
            for l in lis:
                ll = l.split()
                for word in ll:
                    ws = word.split('/')
                    m = en_word_re.match(ws[0])
                    if len(ws) >= 2 and m:
                        thew = m.group()+ws[1].strip()
                        #print type(thew)
                        li.append(thew)
                if len(li) > 3:
                    sens.append(li)
                    i += 1
                else:
                    pass #print l, 
            #if i > 1000:
            #    break
    return sens

def sogou_files():
    copus_sample = '/opt/projects/packages/sogou_corpus/Sample'
    tagger = Tagger()

    for d in os.listdir(copus_sample):
        d1 = os.path.join(copus_sample, d)
        if os.path.isdir(d1):
            for d3 in os.listdir(d1):
                f = os.path.join(d1, d3)
                if os.path.isfile(f):
                    yield f
def save_files():
    files = list(sogou_files())
    num = 6
    per = len(files)/num
    for i in range(num):
        fw = open('sogou_%d'% i, 'w')
        for ff in files[i*per:(i+1)*per]:
            fw.write(ff+'\n')
        fw.close()

def mksogou_(num):
    copus_sample = '/opt/projects/packages/sogou_corpus/Sample'
    print 'processing ', num
    tagger = Tagger()
    fout = codecs.open('sogou_out%d'%num, 'w', 'utf-8')
    with open('sogou_%d'%num) as fw:
        for f in fw:
            with open(f.replace('\n', '')) as file:
                for line in file:
                    content = line.decode('gb2312', 'ignore').encode('utf-8').decode('utf-8', 'replace')
                    line = []
                    for word_pos in tagger.cut_pos(content):
                        m = en_word_re.match(word_pos[0])
                        if m:
                            thew = m.group()+word_pos[1].strip()
                            line.append(thew)
                    if len(line) > 3:
                        fout.write(u' '.join(line)+u'\n')
def mksogou():
    num = 6
    pool = Pool(num)
    print "parnet process (id %s)" % os.getpid()
    pool.map(mksogou_, range(num))
    print "All Done"

def sogou_sents():
    num = 6
    for num in range(num):
        fout = codecs.open('sogou_out%d'%num, 'r', 'utf-8')
        for line in fout:
            line = line.replace(u'\n','')
            #print line.split()
            #yield line.split()
            ll = []
            for w in line.split():
                m = en_word_re.match(w)
                if m:
                    ll.append(m.group())
            if len(ll) > 3:
                yield ll

def train():
    # load up unzipped corpus from http://mattmahoney.net/dc/text8.zip
    #sentences = get_sents()
    sentences = sogou_sents()

    # train the skip-gram model; default window=5
    model = word2vec.Word2Vec(list(sentences), size=200)

    # pickle the entire model to disk, so we can load&resume training later
    model.save('./text9.model')

    # ... and some hours later... just as advertised...
    sims = model.most_similar(positive=[u'女人n', u'国王n'], negative=[u'男人n'], topn=1)
    print sims[0][0]
     

    # store the learned weights, in a format the original C tool understands
    #model.save_word2vec_format('/tmp/text8.model.bin', binary=True)
    # or, import word weights created by the (faster) C word2vec
    # this way, you can switch between the C/Python toolkits easily
    #model = word2vec.Word2Vec.load_word2vec_format('/tmp/vectors.bin',
    #        binary=True)
      
    # "boy" is to "father" as "girl" is to ...?
    #print model.most_similar(['女儿', '父亲'], ['男儿'], topn=3)

def test():
    model = word2vec.Word2Vec.load('./origin/text8.model')
    #sims = model.most_similar(positive=[u'你们', u'你'], negative=[], topn=10)
    #sims = model.most_similar(positive=[u'中国ns', u'足球n'], negative=[u'日本ns'], topn=10)
    #for sim in sims:
    #    print sim[0], sim[1]
    s = u'刚刚,d 甫,v 才,d 新,a 顷,n 刚,d 刚好,nr 正好,z 恰好,n 刚好,nr 恰好,nr 正好,z 刚刚,d 恰,d 刚好,nr 恰好,nr 正好,z 恰,d 刚好,nr 正好,z 恰好,n '
    s = s.replace(',','')

    print model.doesnt_match(s.split())

'''
for s in sogou_sents():
    for ss in s:
        print ss, 
    break
'''
#save_files()
#mksogou()
#sogou_sents()

#train()
test()

