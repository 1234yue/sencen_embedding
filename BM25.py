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
import math
import redis
def save_three_number(x):
    return float(int(x*1000)/1000)

def log(x):
    return math.log(x)

def log_di(x,y):
    return math.log(x)/math.log(y)

def count_word(source_path):
    f = open(source_path,mode = 'r',encoding='utf-8')
    id_count ={}
    d_sum_len = 0
    count = 0
    is_q = True
    try:
        for line in f.readlines():
            if is_q:
                is_q = False
            else:
                is_q = True
                continue
            words = line.strip().split()
            count = count + 1
            d_sum_len = d_sum_len + len(words)
            for word in words:
                if word in id_count:
                    id_count[word] = id_count[word] + 1
                else:
                    id_count[word] = 1
        return id_count,count,d_sum_len
    except:
        print('something wrong in cal idf')
    f.close()

def IDF(id_count,word,N):
    #N = id_count['whole_sum_ount_len']
    nw = id_count.get(word,0)
    up = N - nw + 0.5
    bottom = nw + 0.5
    return log(up/bottom)
def score():
    return
def test(source_path):
    cidian,count,d_sum_len = count_word(source_path)
    '''
    test = '据说 毛主席纪念堂 自 今年 3 月 1 日 开始 到 8 月 31 日 进行 闭馆 整修   期间 不 接待 瞻仰   请问 这是 真的 吗'
    test = test.split()
    for word in test:
        print(IDF(cidian, word),cidian.get(word,0),word)
    '''
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    f = open(source_path,mode = 'r',encoding ='utf-8')
    index = 0
    Q = '毛主席纪念堂 自 今年 进行 闭馆 整修'
    for line in f.readlines():
        index = index + 1
        if index >10:break
        s = score_redis(Q, line,r)
        print(s,line)
    f.close()

def df_into_redis(cidian,N,dlen):
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    len_key='question_all_line_count'
    r.set(len_key,N)
    len_key='question_all_line_len'
    r.set(len_key,dlen)
    for key in cidian:
        value = cidian.get(key,None)
        if not value:
            continue
        else:
            r.set(key+'count',value)
    print('insert is ok')

#calculate R(q,d)
def cal_K(dl , avg_dl,k1 =2,b =0.75):
    return k1*(1-b+b*(dl/avg_dl))

def cal_R(qi,d,avg_dl):
    words = d.split()
    fi = words.count(qi)
    dl = len(words)
    K = cal_K(dl,avg_dl)
    k1 = 2
    return fi*(k1+1)/(fi+K)


#use redis cal BM25
def IDF_redis(r,word):
    #N = id_count['whole_sum_ount_len']
    N = int(str(r.get('question_all_line_count').decode('utf-8')))
    nw = r.get(word+'count')
    if not nw:
        nw = 0
    else:
        nw = int(str(nw.decode('utf-8')))
    up = N - nw + 0.5
    bottom = nw + 0.5
    return log(up/bottom)
def score_redis(Q,d,r):
    count = int(str(r.get('question_all_line_count').decode('utf-8')))
    d_sum_len = int(str(r.get('question_all_line_len').decode('utf-8')))
    qs = Q.split()
    avg_dl = d_sum_len / count
    sum = 0
    for q in qs:
        sum = sum + IDF_redis(r,q) * cal_R(q, d, avg_dl)
    return sum

if __name__ == '__main__':
    '''
    source_path = 'test.txt'
    test(source_path)
    
    
    
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    #print(r.smembers('凤凰古城'))
    #print(str(r.get('凤凰古城hhhhhhhhjueduimeiuyou').decode('utf-8')))
    x = r.get('凤凰古城hhhhhhhhjueduimeiuyou')
    y = r.get('凤凰古城')
    if not x:
        print('it is None')
    print(y.decode('utf-8'))
    '''
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    cidian, count, d_sum_len = count_word('yuliao.txt')
    print(count)
    df_into_redis(cidian, count, d_sum_len)
    print(r.smembers('凤凰古城'))
    print(r.get('凤凰古城count'))
    source_path = 'test.txt'
    #test(source_path)




