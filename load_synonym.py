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

def load_symdict(source_path):
    f=open(source_path,mode = 'r',encoding='utf-8')
    synom={}
    second_index={}
    count = 0
    now_line=''
    try:
        for line in f.readlines():
            kv = line.split(':')
            if len(kv)!=2:continue
            key, value = line.split(':')
            key = key.strip()
            value = value.strip('\n').strip()
            value = re.split(' +|\t+', value)
            if key in synom:
                synom[key] = list(set(synom[key]) | set(value))
            else:
                synom[key] = value
            for x in value:
                if x in second_index:
                    if key not in second_index[x]:
                        second_index[x].append(key)
                else:
                    second_index[x] = []
                    second_index[x].append(key)
            count = count + 1
            now_line = line
    except:
        print(count,now_line)

    f.close()
    return synom,second_index
def test(source_path):
    x,y= load_symdict(source_path)
    count = 0
    print(y.get('建设银行',None),x.get('建行',None))
    for y in x:
        if count >=10: return
        print(y,x[y])
        count = count + 1
if __name__=='__main__':
    test('synonym.txt')