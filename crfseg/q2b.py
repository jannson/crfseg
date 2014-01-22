#!/usr/bin/env
# -*- coding: utf-8 -*-

def strQ2B(ustring):
    """把字符串全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        # 全角字符unicode编码从65281~65374 （十六进制 0xFF01 ~ 0xFF5E）
        # 半角字符unicode编码从33~126 （十六进制 0x21~ 0x7E）
        # 而且除空格外,全角/半角按unicode编码排序在顺序上是对应的
        if inside_code==0x3000:
            # 空格 全角为0x3000 半角为0x0020
            inside_code=0x0020
        elif inside_code == 0x3002:
            # 中文句号
            inside_code=0x2e
        else:
            inside_code-=0xfee0
        if inside_code<0x0020 or inside_code>0x7e:      
            rstring += uchar
        else:
            rstring += unichr(inside_code)
    return rstring

if __name__ == '__main__':
    samples = [
                (u'１２３４５６７８９０',u'1234567890'),
                (u'ａｂｃ１２３４５', u'abc12345'),
                (u'！＠＃％＾＆＊（）＿＋', u'!@#%^&*()_+'),
                (u'［］ＡＢＣＤＥＦＧＨＩＪＫ', u'[]ABCDEFGHIJK'),
                (u'㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩', u'㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩'),
                (u'你啊，。。', u'你啊,..')
            ]

    for (key, value) in samples:
        if strQ2B(key) == value:
            print '%s:%s convert ok!' % (key, value)
        else:
            print '%s:%s convert failure!' % (key, value)

