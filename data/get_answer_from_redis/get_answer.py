# -*- coding: utf-8 -*-
import io
import redis
import jieba
import gzip
import os
import sys
import re
import tarfile
import fileinput

def rm_pun(sencen):
    sen = sencen.strip()
    return re.sub('[+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+', ' ', sen)

def get_answer(sentence):
    sen = rm_pun(sentence)
    #seg_list = [w for w in sen]
    seg_list = jieba.cut(re.sub('(http)+(www)*.*html|(www)+.*.com', '', sen.replace(' ', '')), cut_all=False)
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    mset = set()
    is_empty = True
    for seg in seg_list:
        n_set = r.smembers(seg)
        if is_empty:
            mset = mset | n_set
            is_empty = False
        else:
            # if(mset&n_set!=set()):
            mset = mset & n_set
    count = 0;
    for x in mset:
        count =count +1
        if count >5:
            break
        index = 'Q_' + str(int(x))
        print(r.get(index).decode('utf-8'))
        index = 'A_' + str(int(x))
        print(r.get(index).decode('utf-8'))

def get_answer_add_sym(sentence,cidian,second_index):
    sen = rm_pun(sentence)
    seg_list = jieba.cut(re.sub('(http)+(www)*.*html|(www)+.*.com', '', sen.replace(' ', '')), cut_all=False)
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    mset = set()
    is_empty= True
    for seg in seg_list:
        n_set = r.smembers(seg)
        sym_words =[]
        if seg in cidian:
            sym_words = cidian.get(seg,None)
        elif seg in second_index:
            for x in second_index[seg]:
                seg_equal =x
                sym_words.extend(cidian.get(seg_equal,None))
        sym_words = list(set(sym_words))
        if sym_words:
            for word in sym_words:
                sym_set = r.smembers(word)
                n_set = n_set|sym_set
        if is_empty:
            mset =mset| n_set
            is_empty = False
        else:
            #if(mset&n_set!=set()):
            mset = mset&n_set
    for x in mset:
        index = 'A_'+str(int(x))
        print(r.get(index).decode('utf-8'))
