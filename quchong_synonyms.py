import io
import redis
import jieba
import gzip
import os
import sys
import re
import tarfile
import fileinput
# bing cha ji
def find(x,f):
    if f[x]==x:
      return x
    else:
      f[x]=find(f[x],f)
      return f[x]
def union(l,r,f):
    L = find(l,f)
    R = find(r,f)
    if(L!=R):
        f[L]=R
def get_word_id(source_path):
    f = open(source_path,mode = 'r',encoding = 'utf-8')
    index = 0
    word_id={}
    for line in f.readlines():
        key,values = line.split('->')
        key = key.strip()
        if key not in word_id:
            word_id[key]=index
            index = index + 1
        values =values.split()
        for value in values:
            v = value.split('[')[0]
            if v not in word_id:
                word_id[v] = index
                index = index + 1
    f.close()
    id_word={}
    for key in word_id:
        v = word_id[key]
        id_word[v]=key
    return word_id,id_word
def process(source_path,target_path):
    word_id,id_word= get_word_id(source_path)
    w_len = len(word_id)
    fa=[]
    for i in range(w_len):
        fa.append(i)
    f = open(source_path, mode='r', encoding='utf-8')
    for line in f.readlines():
        key,values = line.split('->')
        key = key.strip()
        l=int(word_id[key])
        values = values.split()
        for value in values:
            v = value.split('[')[0]
            r = int(word_id[v])
            #print(l,r,type(l),type(r))
            union(l,r,fa)
    index = 0
    id_words={}
    for i in range(w_len):
        key = find(i,fa)
        if key not in id_words:
            id_words[key]=[]
        id_words[key].append(i)
    fw = open(target_path,mode = 'w',encoding='utf-8')
    for key in id_words:
        for v in id_words[key]:
            word = id_word[v]
            fw.write(word+' ')
        fw.write('\n')
    fw.close()
    f.close()
def test(x):
    x[0]=3
if __name__=='__main__':
    a=[1,2,3]
    test(a)
    print(a)
    source_path='syms.txt'
    target_path='new.txt'
    process(source_path, target_path)
    print('every thing is ok there are 500000000')