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
from redisset import rm_pun
class BM_answer():

    def __init__(self):
        self.sym_path = '/home/yueshifeng/repos/query_expansion/synonym.txt'
        self.cidian, self.second_index = load_symdict(self.sym_path)

    def get_answer(self, sentence):
        sen = rm_pun(sentence)
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
        candicates = []
        seg_list = jieba.cut(re.sub('(http)+(www)*.*html|(www)+.*.com', '', sen.replace(' ', '')), cut_all=False)
        seg_list = ' '.join(seg_list)
        print(seg_list)

        for x in mset:
            index = 'Q_' + str(int(x))
            candicate = str(r.get(index).decode('utf-8'))
            index = 'A_' + str(int(x))
            ans = str(r.get(index).decode('utf-8'))
            score = score_redis(seg_list, candicate, r)
            candicates.append((candicate, score))
        candicates = sorted(candicates, key=lambda x: -x[1])
        candicates = candicates[:3]

        for x in candicates:
            print(x)
            '''
            print('question and score',x[0],x[1])
            print('answer',x[2])
            '''

        return candicates
    def get_answer_add_sym_and_sort(self ,sentence):
        cidian =self.cidian
        second_index = self.second_index
        sen = rm_pun(sentence)
        seg_list = jieba.cut(re.sub('(http)+(www)*.*html|(www)+.*.com', '', sen.replace(' ', '')), cut_all=False)
        r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        mset = set()
        is_empty = True
        for seg in seg_list:

            n_set = r.smembers(seg)
            sym_words = []
            if seg in cidian:
                sym_words = cidian.get(seg, None)
            elif seg in second_index:
                for x in second_index[seg]:
                    seg_equal = x
                    sym_words.extend(cidian.get(seg_equal, None))
            sym_words = list(set(sym_words))
            if sym_words:
                for word in sym_words:
                    sym_set = r.smembers(word)
                    n_set = n_set | sym_set
            if is_empty:
                mset = mset | n_set
                is_empty = False
            else:
                # if(mset&n_set!=set()):
                mset = mset & n_set
        candicates = []
        seg_list = jieba.cut(re.sub('(http)+(www)*.*html|(www)+.*.com', '', sen.replace(' ', '')), cut_all=False)
        seg_list = ' '.join(seg_list)
        print(seg_list)

        for x in mset:
            index = 'Q_' + str(int(x))
            candicate = str(r.get(index).decode('utf-8'))
            index = 'A_' + str(int(x))
            ans = str(r.get(index).decode('utf-8'))
            score = score_redis(seg_list, candicate, r)
            candicates.append((candicate, score))
        candicates = sorted(candicates, key=lambda x: -x[1])
        candicates = candicates[:3]

        for x in candicates:
            print(x)
            '''
            print('question and score',x[0],x[1])
            print('answer',x[2])
            '''
        return candicates
def data_for_state(source_path,target_path):
    f = open(source_path,mode = 'r',encoding='utf-8')
    fw = open(target_path,mode = 'w',encoding = 'utf-8')
    model = BM_answer()
    for line in f.readlines():
        data = model.get_answer_add_sym_and_sort(line)
        for x in data:
            fw.write(x[0]+'\n')
    fw.close()
    f.close()
if __name__=='__main__':
    model = BM_answer()
    sys.stdout.write('>')
    sys.stdout.flush()
    #data_for_state('test.txt','target.txt')
    sentence = sys.stdin.readline()
    while sentence:
          model.get_answer_add_sym_and_sort(sentence)
          print('begin no synonym')
          model.get_answer(sentence)
          sys.stdout.write('>')
          sys.stdout.flush()
          sentence = sys.stdin.readline()