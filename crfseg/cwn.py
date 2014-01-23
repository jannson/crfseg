#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Chinese Wordnet """

import codecs, sys, os
#import MySQLdb
import sqlite3
from opencc import OpenCC, DictType
import re

path1 = ['simp_to_trad_characters.ocd', 'simp_to_trad_phrases.ocd']
path2 = ['trad_to_simp_characters.ocd', 'trad_to_simp_phrases.ocd']
def simp2trad(s):
    with OpenCC() as cc:
        for p in path1:
            cc.dict_load(p, DictType.DATRIE)
        return cc.convert(s)

def trad2simp(s):
    with OpenCC() as cc:
        for p in path2:
            cc.dict_load(p, DictType.DATRIE)
        return cc.convert(s)

'''
conn = MySQLdb.connect(host = 'localhost',
                       user = 'root',
                       charset = 'utf8',
                       passwd = '751130',
                       db = 'cwn') # connect to my_laptop SQL
'''

the_file = os.path.dirname(os.path.abspath(__file__))
the_file = os.path.join(the_file,'..','origin','output.sqlite')
conn = sqlite3.connect(the_file)

cursor = conn.cursor()

#iden = '真1.v.0310'   #lemma---------antonyms()
#iden = '骯髒.v.0101'  #facet---------antonyms() + senses

#iden = '不加.d.0100'  #--------------hypernyms() + senses
#iden = '勿.d.0200'    #--------------hyponyms()
#iden = '代1.n.0810'   #--------------holonyms()
#iden = '朝代.n.0100'  #--------------meronyms()

###################################################################################
###########################  CLASS < SYNSET > #####################################
###################################################################################
class Synset(object):
    """ synonym set """

    def __init__(self,iden='朝代.n.0100'):

       ################################# DEFINITION ##########################
       lemmaName = iden[:-7]
       self.id = iden
       self.lemma = lemmaName
       cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
       lemmaId = cursor.fetchall() # 6 digits
       #print lemmaId  #((u'070301',),) type:unicode
       senseId = lemmaId[0][0] + iden[-4:-2]
       #print senseId # unicode
       cursor.execute("SELECT sense_def FROM cwn_sense WHERE sense_id = '"+senseId+"' UNION SELECT sense_def FROM cwn_sensetmp WHERE sense_tmpid = '"+senseId+"'")
       definitions = cursor.fetchall()
       #print definitions
       defin = definitions[0][0]#.encode('utf8')
       self.definition = defin

       ################################# SENSES (synset members) ###############
       if iden[-1] != '0': # 義面
           selfId = lemmaId[0][0] + iden[-4:]
       else: # 詞義
           selfId = lemmaId[0][0] + iden[-4:-2]
       print 'selfid ', selfId
       cursor.execute("SELECT synonym_word, ref_id FROM cwn_synonym WHERE cwn_id ='"+selfId+"' UNION SELECT synonym_word, ref_id FROM cwn_synotmp WHERE cwn_tmpid ='"+selfId+"' UNION SELECT var_word, ref_id FROM cwn_vartmp WHERE cwn_tmpid ='"+selfId+"' UNION SELECT var_word, ref_id FROM cwn_vartmp WHERE cwn_tmpid ='"+selfId+"'");
       all_tuple = cursor.fetchall()
       #print all_tuple # (u'\u524d\u65b9', u'0100')
       if len(all_tuple) == 0:
           sense1 = []
       else:
           sense1 = []
           for tup in all_tuple:
               member = tup[0]+'..'+ tup[1]
               sense1.append(member)
       #### insert pos tag
       pos = []
       for a in sense1:
           lemmaName = a[:-6]
           refId = a[-4:-2]
           ###############  找出sense_id  ###########################################   
           cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
           lemmaId = cursor.fetchall()
           #print lemmaId  #((u'070301',),) type:unicode
           senseid = lemmaId[0][0] + refId
           cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+senseid+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+senseid+"'")
           tag = cursor.fetchall()
           if len(tag) == 0:
               pos = '?'
           else:
               pos.append(tag[0][0][0].lower())
       index = [a.find('.') for a in sense1]
       senses = []
       for n in range(len(pos)):
           senses.append(sense1[n][:index[n]+1]+pos[n]+sense1[n][index[n]+1:])
       self.senses = senses        

##################################    ANTONYMS   #######################################
########################################################################################
    def antonyms(self):
        ################ GET SENSE-ID #############################
        cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+self.lemma+"'")
        lemmaId = cursor.fetchall()
        #print lemmaId  #((u'070301',),) type:
        if self.id[-1] != '0': # 義面
           selfId = lemmaId[0][0] + self.id[-4:]
        else: # 詞義
           selfId = lemmaId[0][0] + self.id[-4:-2]

        ############# GET XXXnym/ref_id BY MATCHING CWN_ID #########
        cursor.execute("SELECT antonym_word, ref_id FROM cwn_antonym WHERE cwn_id ='"+selfId+"' UNION SELECT antonym_word, ref_id FROM cwn_antotmp WHERE cwn_tmpid ='"+selfId+"'")
        all_tuple = cursor.fetchall()
        #print all_tuple # (u'\u524d\u65b9', u'0100')
        if len(all_tuple) == 0:
            nyms = []
        else:
            nyms = []
            for tup in all_tuple:
                member = tup[0].encode('utf8')+'..'+ str(tup[1])
                nyms.append(member)
        nyms.sort()
        #print nyms
        # insert pos tag
        pos = []
        for a in nyms:
            lemmaName = a[:-6]
            refId = a[-4:-2]
            ###############  找出sense_id  ###########################################   
            cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
            lemmaId = cursor.fetchall()
            #print lemmaId  #((u'070301',),) type:unicode
            senseid = lemmaId[0][0] + refId
            cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+senseid+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+senseid+"'")
            tag = cursor.fetchall()
            if len(tag) == 0:
                pos = '?'
            else:
                pos.append(tag[0][0][0].lower())
        index = [a.find('.') for a in nyms]
        antonyms = []
        for n in range(len(pos)):
            antonyms.append(str(nyms[n][:index[n]+1])+str(pos[n])+str(nyms[n][index[n]+1:]))
        return antonyms

###################################    HYPERNYMS      ###################################
#########################################################################################            
    def hypernyms(self):
        ################ GET SENSE-ID #############################
        cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+self.lemma+"'")
        lemmaId = cursor.fetchall()
        if self.id[-1] != '0': # 義面
           selfId = lemmaId[0][0] + self.id[-4:]
        else: # 詞義
           selfId = lemmaId[0][0] + self.id[-4:-2]

        ############# GET XXXnym/ref_id BY MATCHING CWN_ID #########
        cursor.execute("SELECT up_word, ref_id FROM cwn_upword WHERE cwn_id ='"+selfId+"' UNION SELECT up_word, ref_id FROM cwn_uptmp WHERE cwn_tmpid ='"+selfId+"'")
        all_tuple = cursor.fetchall()
        #print all_tuple # (u'\u524d\u65b9', u'0100')
        if len(all_tuple) == 0:
            nyms = []
        else:
            nyms = []
            for tup in all_tuple:
                member = tup[0].encode('utf8')+'..'+ str(tup[1])
                nyms.append(member)
        nyms.sort()

        # insert pos tag
        pos = []
        for a in nyms:
            lemmaName = a[:-6]
            refId = a[-4:-2]
            ###############  找出sense_id  ###########################################   
            cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
            lemmaId = cursor.fetchall()
            #print lemmaId  #((u'070301',),) type:unicode
            senseid = lemmaId[0][0] + refId
            cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+senseid+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+senseid+"'")
            tag = cursor.fetchall()
            if len(tag) == 0:
                pos = '?'
            else:
                pos.append(tag[0][0][0].lower())
        index = [a.find('.') for a in nyms]
        hypernyms = []
        for n in range(len(pos)):
            hypernyms.append(str(nyms[n][:index[n]+1])+str(pos[n])+str(nyms[n][index[n]+1:]))
        return hypernyms


#################################    HYPONYMS      ###################################
#######################################################################################
    def hyponyms(self):
        ################ GET SENSE-ID #############################
        cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+self.lemma+"'")
        lemmaId = cursor.fetchall()
        if self.id[-1] != '0': # 義面
           selfId = lemmaId[0][0] + self.id[-4:]
        else: # 詞義
           selfId = lemmaId[0][0] + self.id[-4:-2]

        ############# GET XXXnym/ref_id BY MATCHING CWN_ID #########
        cursor.execute("SELECT hypo_word, ref_id FROM cwn_hypo WHERE cwn_id ='"+selfId+"' UNION SELECT hypo_word, ref_id FROM cwn_hypotmp WHERE cwn_tmpid ='"+selfId+"'")
        all_tuple = cursor.fetchall()
        #print all_tuple # (u'\u524d\u65b9', u'0100')
        if len(all_tuple) == 0:
            nyms = []
        else:
            nyms = []
            for tup in all_tuple:
                member = tup[0].encode('utf8')+'..'+ str(tup[1])
                nyms.append(member)
        nyms.sort()
        # insert pos tag
        pos = []
        for a in nyms:
            lemmaName = a[:-6]
            refId = a[-4:-2]
            ###############  找出sense_id  #####################   
            cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
            lemmaId = cursor.fetchall()
            #print lemmaId  #((u'070301',),) type:unicode
            senseid = lemmaId[0][0] + refId
            cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+senseid+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+senseid+"'")
            tag = cursor.fetchall()
            if len(tag) == 0:
                pos = '?'
            else:
                pos.append(tag[0][0][0].lower())
        index = [a.find('.') for a in nyms]
        hyponyms = []
        for n in range(len(pos)):
            hyponyms.append(str(nyms[n][:index[n]+1])+str(pos[n])+str(nyms[n][index[n]+1:]))
        return hyponyms


##############################    HOLONYMS      ###################################
#######################################################################################
    def holonyms(self):
        ################ GET SENSE-ID #############################
        cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+self.lemma+"'")
        lemmaId = cursor.fetchall()
        if self.id[-1] != '0': # 義面
           selfId = lemmaId[0][0] + self.id[-4:]
        else: # 詞義
           selfId = lemmaId[0][0] + self.id[-4:-2]

        ############# GET XXXnym/ref_id BY MATCHING CWN_ID #########
        cursor.execute("SELECT holo_word, ref_id FROM cwn_holo WHERE cwn_id ='"+selfId+"' UNION SELECT holo_word, ref_id FROM cwn_holotmp WHERE cwn_tmpid ='"+selfId+"'")
        all_tuple = cursor.fetchall()
        #print all_tuple # (u'\u524d\u65b9', u'0100')
        if len(all_tuple) == 0:
            nyms = []
        else:
            nyms = []
            for tup in all_tuple:
                member = tup[0].encode('utf8')+'..'+ str(tup[1])
                nyms.append(member)
        nyms.sort()
        # insert pos tag
        pos = []
        for a in nyms:
            lemmaName = a[:-6]
            refId = a[-4:-2]
            ###############  找出sense_id  #####################   
            cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
            lemmaId = cursor.fetchall()
            #print lemmaId  #((u'070301',),) type:unicode
            senseid = lemmaId[0][0] + refId
            cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+senseid+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+senseid+"'")
            tag = cursor.fetchall()
            if len(tag) == 0:
                pos = '?'
            else:
                pos.append(tag[0][0][0].lower())
        index = [a.find('.') for a in nyms]
        holonyms = []
        for n in range(len(pos)):
            holonyms.append(str(nyms[n][:index[n]+1])+str(pos[n])+str(nyms[n][index[n]+1:]))
        return holonyms

##############################    MERONYMS      #######################################
#######################################################################################
    def meronyms(self):
        ################ GET SENSE-ID #############################
        cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+self.lemma+"'")
        lemmaId = cursor.fetchall()
        if self.id[-1] != '0': # 義面
           selfId = lemmaId[0][0] + self.id[-4:]
        else: # 詞義
           selfId = lemmaId[0][0] + self.id[-4:-2]


        ############# GET XXXnym/ref_id BY MATCHING CWN_ID #########
        cursor.execute("SELECT mero_word, ref_id FROM cwn_mero WHERE cwn_id ='"+selfId+"' UNION SELECT mero_word, ref_id FROM cwn_merotmp WHERE cwn_tmpid ='"+selfId+"'")
        all_tuple = cursor.fetchall()
        #print all_tuple # (u'\u524d\u65b9', u'0100')
        if len(all_tuple) == 0:
            nyms = []
        else:
            nyms = []
            for tup in all_tuple:
                member = tup[0].encode('utf8')+'..'+ str(tup[1])
                nyms.append(member)
        nyms.sort()
        # insert pos tag
        pos = []
        for a in nyms:
            lemmaName = a[:-6]
            refId = a[-4:-2]
            ###############  找出sense_id  #####################   
            cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
            lemmaId = cursor.fetchall()
            #print lemmaId  #((u'070301',),) type:unicode
            senseid = lemmaId[0][0] + refId
            cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+senseid+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+senseid+"'")
            tag = cursor.fetchall()
            if len(tag) == 0:
                pos = '?'
            else:
                pos.append(tag[0][0][0].lower())
        index = [a.find('.') for a in nyms]
        meronyms = []
        for n in range(len(pos)):
            meronyms.append(str(nyms[n][:index[n]+1])+str(pos[n])+str(nyms[n][index[n]+1:]))
        return meronyms

###################################################################################
###########################  CLASS < SENSE > ######################################
###################################################################################
class Sense(object):
    """ Chinese Wordnet senses """
    
    def __init__(self, iden='晨間.n.0100'):
        ####################################      NAME     ##################
        lemmaName = iden[:-7]#用regex把後面數字去掉?How?
        self.name = lemmaName
        
        #################################### PRONUNCIATION, KEY(SENSE_ID) ##################
        cursor.execute("SELECT cwn_pinyin, cwn_zhuyin, lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
        sound_key = cursor.fetchall()
        self.pinyin = sound_key[0][0]#.encode('utf8') #加不加?
        #print self.pinyin
        self.zhuyin = sound_key[0][1]#.encode('utf8')
        #print self.zhuyin
        senseId = sound_key[0][2] + iden[-4:-2]
        self.key = senseId#.encode('utf8')
        #print senseId
        ##################################### DEFINITION  & DOMAIN #####################
        cursor.execute("SELECT sense_def, domain_id FROM cwn_sense WHERE sense_id = '"+senseId+"' UNION SELECT sense_def, domain_id FROM cwn_sensetmp WHERE sense_tmpid = '"+senseId+"'")
        definition_domain = cursor.fetchall()
        defin = definition_domain[0][0]
        self.definition = defin#.encode('utf8')
        #print defin
        domain = definition_domain[0][1] #str if found
        if domain == None: # no domain
            domain = []
        else:
            if domain.find(u'\uff20') == -1: #only one domain
                domain = domain
            else:
                domain = domain.split(u'\uff20') #multiple domains ＠
        self.domain = domain#.encode('utf8')

        ######################################## TRANSLATION #############################
        cursor.execute("SELECT synset_word1, synset_offset, synset_cwnrel, synset_trans FROM cwn_synset WHERE cwn_id = '"+senseId+"'")
        rows = cursor.fetchall() #((u'new', u'01581807A', u'\u4e0a\u4f4d\u8a5e', u''),)
        if len(rows) == 0: #if there's no translation
            translation = []
        else:
            lis = []
            for row in rows:
                for unit in row:
                    if unit == None:
                        unit = ''
                        lis.append(unit)
                    else:
                        lis.append(unit)
        translation = []
        unit = lis[0]+'.'+lis[1]+'.'+lis[2]+'.'+lis[3]
        translation.append(unit)
        self.wn_trans = translation

        ################################### EXAMPLES #####################################
        cursor.execute("SELECT example_cont FROM cwn_example WHERE cwn_id LIKE '"+senseId+"' UNION SELECT example_cont FROM example_tmp WHERE cwn_tmpid LIKE '"+senseId+"'")
        all_examples = cursor.fetchall()
        eg = []
        if len(all_examples) == 0: #no examples
            if self.key[-1] != '0': # examples go under facets
                print "This sense has facets. Please refer to the facets for examples."
            else:   # database no examples
                eg = []
        else:
            for a in all_examples:
                eg.append(a[0])        
        self.examples = eg
        
        ################################## PARONYMS ######################################
        """iden='晨間.n.0100'"""
        # attributes 及 methods 的差別?  
        ''' TODO what is it?
        cursor.execute("SELECT paranym_word, ref_id FROM cwn_paranym WHERE cwn_id ='"+senseId+"' UNION SELECT paranym_word, ref_id FROM cwn_paranymtmp WHERE cwn_tmpid ='"+senseId+"'")
        all_tuple = cursor.fetchall()
        #print all_tuple # (u'\u524d\u65b9', u'0100')
        paronyms = []
        if len(all_tuple) == 0:
            paronyms = []
        else:
            paronym = []
            for tup in all_tuple:
                member = tup[0].encode('utf8')+'..'+ str(tup[1])
                paronym.append(member)
            for a in paronym:
                paronyms.append(a[:-5]+iden[-6]+a[-5:])      
        self.paronyms = paronyms
        '''


###################################################################################
###########################  CLASS < FACET > ######################################
###################################################################################
class Facet(object):
    """ Chinese Wordnet facets """

    def __init__(self, iden='喜.v.0201'):
        ####################################      NAME     ##################
        lemmaName = iden[:-7]#用regex把後面數字去掉?How?
        self.name = lemmaName

        #################################### PRONUNCIATION, KEY(SENSE_ID) ##################
        cursor.execute("SELECT cwn_pinyin, cwn_zhuyin, lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
        sound_key = cursor.fetchall()
        self.pinyin = sound_key[0][0]#.encode('utf8') #加不加?
        #print self.pinyin
        self.zhuyin = sound_key[0][1]#.encode('utf8')
        #print self.zhuyin
        facetId = sound_key[0][2] + iden[-4:-2]+'0'+iden[-1]
        #print facetId
        self.key = facetId#.encode('utf8')

        ##################################### DEFINITION  & DOMAIN #####################
        cursor.execute("SELECT facet_def, domain_id FROM cwn_facet WHERE facet_id = '"+facetId+"' UNION SELECT facet_def, domain_id FROM cwn_facettmp WHERE facet_tmpid = '"+facetId+"'")
        definition_domain = cursor.fetchall()
        defin = definition_domain[0][0]
        self.definition = defin#.encode('utf8')
        #print defin
        domain = definition_domain[0][1] #str if found
        if domain == None: # no domain
            domain = []
        else:
            if domain.find(u'\uff20') == -1: #only one domain
                domain = domain
            else:
                domain = domain.split(u'\uff20') #multiple domains ＠
        self.domain = domain#.encode('utf8')

        ######################################## TRANSLATION #############################
        #print facetId
        cursor.execute("SELECT synset_word1, synset_offset, synset_cwnrel, synset_trans FROM cwn_synset WHERE cwn_id = '"+facetId+"'")
        rows = cursor.fetchall() #((u'new', u'01581807A', u'\u4e0a\u4f4d\u8a5e', u''),)
        #print rows
        lis = []
        translation = []
        if len(rows) == 0: #if there's no translation
            translation = []
        else:
            for row in rows:
                for unit in row:
                    if unit == None:
                        unit = ''
                        lis.append(unit)
                    else:
                        lis.append(unit)
            chunk = lis[0]+'.'+lis[1]+'.'+lis[2]+'.'+lis[3]
            translation.append(chunk)
        self.wn_trans = translation

        ################################### EXAMPLES #####################################
        cursor.execute("SELECT example_cont FROM cwn_example WHERE cwn_id = '"+facetId+"' UNION SELECT example_cont FROM example_tmp WHERE cwn_tmpid = '"+facetId+"'")
        all_examples = cursor.fetchall()
        eg = []
        for a in all_examples:
            eg.append(a[0])
        #for a in eg:
         #   print a.encode('utf8')
        self.examples = eg

        ################################## PARONYMS ######################################
        """iden='怒.v.0101'"""
        cursor.execute("SELECT paranym_word, ref_id FROM cwn_paranym WHERE cwn_id ='"+facetId+"' UNION SELECT paranym_word, ref_id FROM cwn_paranymtmp WHERE cwn_tmpid ='"+facetId+"'")
        all_tuple = cursor.fetchall()
        #print all_tuple # (u'\u524d\u65b9', u'0100')
        nyms = []
        if len(all_tuple) == 0:
            paronyms = nyms
        else:
            for tup in all_tuple:
                member = tup[0].encode('utf8')+'..'+ str(tup[1])
                nyms.append(member)
            pos = []
            ############## find facet_id ################
            for a in nyms: #nyms ['\xe5\x96\x9c..0201', '\xe5\x93\x801..0111', ...]
                lemmaName = a[:-6]
                refId = a[-4:]#facet level
                cursor.execute("SELECT lemma_id FROM lemma WHERE cwn_lemma = '"+lemmaName+"'")
                lemmaId = cursor.fetchall()
                #print lemmaId  #((u'070301',),) type:unicode
                facetId = lemmaId[0][0] + refId     
            ############## get POS ######################
                cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+facetId+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+facetId+"'")
                tag = cursor.fetchall()
                #print tag #((u'Ncd',),)
                if len(tag) == 0:
                    pos.append(unicode(iden[-6]))
                else:
                    pos.append(tag[0][0][0].lower())
            #print pos
            ######## 將POS 插入 lemma與ID之中 ############
            index = [a.find('.') for a in nyms]
            #print index
            paronyms = []
            for n in range(len(pos)):
                paronyms.append(str(nyms[n][:index[n]+1])+str(pos[n])+str(nyms[n][index[n]+1:]))
        #for a in paranyms:
         #   print a
        self.paronyms = paronyms


###################################################################################
###########################  SYNSET QUERY  ########################################
###################################################################################

def synsets(userInput):
    u_input = userInput.decode('cp950') # why 'ascii' produces Errors???
    userinput = u_input.encode('utf8') # 這邊decode, encode是必要的
    #############   找ref_id    ####################################
    cursor.execute("SELECT sence_id, lemma_id FROM lemma1 WHERE lemma = '"+userinput+"'")
    # 前後要加+ 表示是字串, 在python裡就會被解讀為variable
    #cursor.execute("SELECT cwn_lemma FROM lemma WHERE lemma_id = '100155'")
    sense_lemma = cursor.fetchall() # fetch all matches: ((,...),...)包兩層的tuple
    #print sense_lemma, len(sense_lemma)
    sense_id = []
    lemma_id = []
    for (sense,lemma) in sense_lemma:
        sense_id.append(sense) ## 有了sense_id
        lemma_id.append(str(int(lemma)))
    #print 'sense_id=',sense_id
    #print 'lemma_id=',lemma_id
    ref_id = []
    for a in sense_id:
            if len(a) == 10:
                    refid = a[-4:]
            else:
                    refid = a[-2:]+'00'
            ref_id.append(refid)
    #print refId
    refId = []
    for n in range(len(ref_id)):
        final_ref = ref_id[n][-4:-2]+lemma_id[n]+ref_id[n][-1]
        refId.append(final_ref)
    ###############  用sense_id 找POS  #######################################
    POS = []
    for a in sense_id:
        #cursor.execute("SELECT a.pos  FROM pos a, postmp b WHERE a.cwn_id = '06708104' OR b.cwn_id = '06708104'")
        #cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+a.encode('utf8')+"'")
        cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+a+"'")
        #cursor.execute("SELECT pos FROM pos WHERE cwn_id = '06566503'")
        pos_tag = cursor.fetchall()
        #POS.append(pos_tag[0][0]) # 細詞類
        # type(pos_tag) ----tuple
        if len(pos_tag) == 0:
            cursor.execute("SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+a+"'")
            pos_tag = cursor.fetchall()
            #print pos_tag
            if len(pos_tag) == 0:
                pos_tag = '?'
            else:
                POS.append(pos_tag[0][0][0].lower())
        else:
            POS.append(pos_tag[0][0][0].lower()) # 粗詞類
    #print 'POS=', POS

    #######################    SYNSET IDENTIFIER LIST  ################################
    """ user_input+ref_id[2]\.pos\.ref_id """

    synset_iden = []
    for num in range(len(POS)):
        if refId[num][2] == u'0':
            member = userinput + '.' + (POS[num] + '.' + refId[num]).encode('utf8')
        else:
            member = userinput + str(refId[num][2])+'.' + (POS[num] + '.' + refId[num]).encode('utf8')
        synset_iden.append(member)
    synset_iden.sort()
    return synset_iden
    ######################      SYNSET OBJECT LIST    ##################################
    #synsets = []
    #for idenn in synset_iden:
     #   synsets.append(Synset(idenn))
    #return synsets

def test1():
    iden = '看见'
    iden = simp2trad(iden)+'.n.0100'
    print 'iden ', iden
    #iden = '真1.v.0310'   #lemma---------antonyms()
    #iden = '骯髒.v.0101'  #facet---------antonyms() + senses
    #iden = '不加.d.0100'  #--------------hypernyms() + senses
    #iden = '勿.d.0200'    #--------------hyponyms()
    #iden = '代1.n.0810'   #--------------holonyms()
    #iden = '朝代.n.0100'  #--------------meronyms()
    #iden = '晨間.n.0100'
    #iden = '是2.i.0200'
    set_tmp = Synset(iden=iden)
    print set_tmp.id
    print set_tmp.lemma
    print set_tmp.definition
    print 'sense ',
    for s in set_tmp.senses:
        print s, " ",
    print '\n'
    print 'antonyms', 
    for s in set_tmp.antonyms():
        print s, " ",
    print '\nhypernyms',
    for s in set_tmp.hypernyms():
        print s, " ",
    print '\nhyponyms',
    for s in set_tmp.hyponyms():
        print s, " ",
    print '\n'
    print set_tmp.holonyms()
    for s in set_tmp.meronyms():
        print s, " ",
    print '\n'

    print 'Begin sense'
    sen = Sense(iden=iden)
    print trad2simp(sen.name), sen.key, sen.pinyin, sen.zhuyin, sen.definition, sen.domain, sen.wn_trans
    print '\nexamples ',
    for s in sen.examples:
        print s, " ",
    #print sen.paronyms

import datrie
import zerorpc

def test2():
   trans = zerorpc.Client("tcp://0.0.0.0:3333", timeout=10000)
   en_word_re = re.compile(r'[a-zA-Z]+', re.I|re.U)
   trie = datrie.Trie(ranges=[('0','9'), (u'\u4e00', u'\u9fff')])
   synos_dict = {}
   sens_dict = {}
   groups = []
   logfile = codecs.open('zzz', 'w', 'utf-8')

   select = "SELECT cwn_id, synonym_word, ref_id FROM cwn_synonym UNION SELECT cwn_tmpid, synonym_word, ref_id FROM cwn_synotmp UNION SELECT cwn_id, var_word, ref_id FROM cwn_varword UNION SELECT cwn_tmpid, var_word, ref_id FROM cwn_vartmp"
   all_synos = []
   for s in select.split('UNION'):
       cursor.execute(s)
       all = cursor.fetchall()
       all_synos += all
   #cursor.execute("SELECT cwn_id, synonym_word, ref_id FROM cwn_synonym UNION SELECT cwn_tmpid, synonym_word, ref_id FROM cwn_synotmp UNION SELECT cwn_id, var_word, ref_id FROM cwn_varword UNION SELECT cwn_tmpid, var_word, ref_id FROM cwn_vartmp")
   #cursor.execute("SELECT cwn_id, synonym_word, ref_id FROM cwn_synonym")
   #all_synos = cursor.fetchall()
   print 'len ', len(all_synos)
   for syno in all_synos:
       senseid = syno[0]
       cursor.execute("SELECT lemma_id, cwn_lemma FROM cwn_lemma WHERE cwn_lemma = '"+syno[1]+"'")
       sy = cursor.fetchall() # 6 digits
       if len(sy) == 0 or not syno[2]:
           continue
       sy_sense = sy[0][0]
       sy_sense += syno[2]
       cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+sy_sense+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+sy_sense+"'")
       tag = cursor.fetchall()
       pos = '?'
       if len(tag) > 0:
           pos = tag[0][0].lower()
       #print sy_sense, syno[1], pos
       sy = (sy_sense, syno[1], pos)
       if senseid in synos_dict:
           synos_dict[senseid].append(sy)
       else:
           cursor.execute("SELECT cwn_lemma FROM cwn_lemma WHERE lemma_id = '"+senseid[:6]+"'")
           lemma = cursor.fetchall()
           if len(lemma) == 0:
               synos_dict[senseid] = [sy]
               continue
           this_name = lemma[0][0]
           cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+senseid+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+senseid+"'")
           tag = cursor.fetchall()
           this_pos = '?'
           if len(tag) > 0:
               this_pos = tag[0][0].lower()
           #print senseid, this_name, this_pos
           this_word = (senseid, this_name, this_pos)
           synos_dict[senseid] = [this_word, sy]
   for senseid in synos_dict.keys():
       synos = synos_dict[senseid]
       group = -1
       for word in synos:
           if word[0] in sens_dict:
               group = sens_dict[word[0]]
               break
       if group == -1:
           group = len(groups)
           groups.append([])

       for word in synos:
           if word[0] in sens_dict and sens_dict[word[0]] != group:
               logfile.write(u'WARNING %s %d' % (word[1], group))
           if word[0] not in sens_dict:
               sens_dict[word[0]] = group
               groups[group].append(word)
   i = 0
   for g in groups:
       logfile.write(u"\n\ngroup %d: " % i)
       for w in g:
           logfile.write(u" (%s,%s,%s) " % (w[0], trans.trad2simp(w[1].encode('utf-8')).decode('utf-8'), w[2]))
       i += 1

def test3():
   trans = zerorpc.Client("tcp://0.0.0.0:3333", timeout=10000)
   en_word_re = re.compile(r'[a-zA-Z]+', re.I|re.U)
   sens = {}
   trie = datrie.Trie(ranges=[('0','9'), (u'\u4e00', u'\u9fff')])

   cursor.execute("SELECT lemma_id, cwn_lemma FROM cwn_lemma")
   lemmas = cursor.fetchall() # 6 digits
   for lem in lemmas:
       print 'lem', lem[1]
       cursor.execute("SELECT sense_id FROM cwn_sense UNION SELECT sense_tmpid FROM cwn_sensetmp")
       sns = cursor.fetchall()
       for sn in sns:
           senseid = sn[0]
           cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+senseid+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+senseid+"'")
           tag = cursor.fetchall()
           pos = '?'
           if len(tag) > 0:
               pos = tag[0][0].lower()
           print 'pos', pos
           word = [lem[0], lem[1], sn[0], pos]
           selfId = senseid
           cursor.execute("SELECT synonym_word, ref_id FROM cwn_synonym WHERE cwn_id ='"+selfId+"' UNION SELECT synonym_word, ref_id FROM cwn_synotmp WHERE cwn_tmpid ='"+selfId+"' UNION SELECT var_word, ref_id FROM cwn_vartmp WHERE cwn_tmpid ='"+selfId+"' UNION SELECT var_word, ref_id FROM cwn_vartmp WHERE cwn_tmpid ='"+selfId+"'");
           synos = cursor.fetchall()
           sense1 = []
           print synos
           if len(synos) != 0:
               for tup in synos:
                   if not tup[1]:
                       continue
                   member = tup[0]+'..'+ tup[1]
                   sense1.append(member)
           #### insert pos tag
           pos = []
           for a in sense1:
               lemmaName = a[:-6]
               refId = a[-4:-2]
               ###############  找出sense_id  ###########################################   
               cursor.execute("SELECT lemma_id FROM cwn_lemma WHERE cwn_lemma = '"+lemmaName+"'")
               lemmaId = cursor.fetchall()
               #print lemmaId  #((u'070301',),) type:unicode
               if len(lemmaId) <= 0:
                   continue
               senseid = lemmaId[0][0] + refId
               cursor.execute("SELECT pos FROM pos WHERE cwn_id = '"+senseid+"' UNION SELECT pos FROM pos_tmp WHERE cwn_tmpid = '"+senseid+"'")
               tag = cursor.fetchall()
               if len(tag) == 0:
                   pos = '?'
               else:
                   pos.append(tag[0][0][0].lower())
           index = [a.find('.') for a in sense1]
           senses = []
           for n in range(len(pos)):
               senses.append(sense1[n][:index[n]+1]+pos[n]+sense1[n][index[n]+1:])
       break

if __name__ == "__main__":
   test2()
