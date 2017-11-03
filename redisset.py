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
from load_synonym import load_symdict
from BM25 import score_redis
def insert_set_into_redis(r,key,value):
    for v in value:
        r.sadd(key, v)
def insert_in_to_redis(key,value,r):
    r.set(key, value)


def all_in_redis(source_path):
    f = open(source_path, mode ="r",encoding="utf-8")
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    index = 0
    q=True
    for line in f.readlines():
        key = ''
        if q:
            key = 'Q_'+str(index)
        else:
            key = 'A_'+str(index)
            index = index + 1
        insert_in_to_redis(key,line,r)
        q = not q
    f.close()
def build_inverted_index(source_path):
    f = open(source_path, mode="r", encoding="utf-8")
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    q = True
    index =0
    for line in f.readlines():
        if q:
            words = line.split()
            for word in words:
                r.sadd(word,index)
        else:
            index = index + 1
        q = not q
    f.close()

def rm_pun(sencen):
    sen = sencen.strip()
    return re.sub('[+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+', ' ', sen)

def get_answer(sentence):
    sen = rm_pun(sentence)
    seg_list = jieba.cut(re.sub('(http)+(www)*.*html|(www)+.*.com', '', sen.replace(' ', '')), cut_all=False)
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    mset = set()
    is_empty= True
    for seg in seg_list:
        n_set = r.smembers(seg)
        if is_empty:
            mset =mset| n_set
            is_empty = False
        else:
            #if(mset&n_set!=set()):
            mset = mset&n_set
    for x in mset:
        index = 'A_'+str(int(x))
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

def get_answer_add_sym_and_sort(sentence,cidian,second_index):
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
    candicates = []
    seg_list = jieba.cut(re.sub('(http)+(www)*.*html|(www)+.*.com', '', sen.replace(' ', '')), cut_all=False)
    seg_list =' '.join(seg_list)
    print(seg_list)
    for x in mset:
        index = 'A_'+str(int(x))
        candicate = str(r.get(index).decode('utf-8'))
        score = score_redis(seg_list,candicate,r)
        candicates.append((candicate,score))
    candicates = sorted(candicates, key=lambda x: -x[1])
    num = 0
    for x in candicates:
        if num >=3:break
        num = num + 1
        print(x)

if __name__=='__main__':

    '''
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    pre = '/home/yueshifeng/repos/query_expansion/'
    source_path = pre + 'yuliao.txt'
    all_in_redis(source_path)
    build_inverted_index(source_path)
    print('invert_index is ok')
    
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    value =[1,2,3]
    key ='yue'
    
    insert_set_into_redis(r, key, value)
    a=r.smembers(key)
    print(a,type(a))
    b=[]
    for x in a:
        b.append(int(x))
    print(b)
    r.set('岳','世峰 哈哈 ， 是这样子的' )
    print(r.get('岳').decode('utf-8'))
    
    
    print(r.smembers('凤凰古城'))
    print(r.get('Q_10').decode('utf-8'))
    print(r.get('A_10').decode('utf-8'))
    '''
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    pre = '/home/yueshifeng/repos/query_expansion/'
    source_path = pre + 'yuliao.txt'
    all_in_redis(source_path)
    build_inverted_index(source_path)
    print('invert_index is ok')
    print(r.smembers('凤凰古城'))
    '''
    source_dict_path='/home/yueshifeng/repos/query_expansion/synonym.txt'
    cidian ,second_index= load_symdict(source_dict_path)
    sys.stdout.write('>')
    sys.stdout.flush()
    sentence = sys.stdin.readline()
    #print(r.smembers('凤凰古城'))
    while sentence:
          seg_list = jieba.cut(re.sub('(http)+(www)*.*html|(www)+.*.com', '', sentence.replace(' ', '')), cut_all=False)
          sentence = ' '.join(seg_list)
          get_answer_add_sym_and_sort(sentence,cidian,second_index)
          print('every thing is ok')
          #get_answer(sentence)
          sys.stdout.write('>')
          sys.stdout.flush()
          sentence = sys.stdin.readline()
    '''
