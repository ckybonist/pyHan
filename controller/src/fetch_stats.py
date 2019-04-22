#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import json
import redis
from datetime import datetime
from collections import defaultdict
from collections import OrderedDict


HOME = os.environ['HOME']
now = datetime.now()
iso_now = datetime.isocalendar(now)


""" Fetch N-grams stats """

class DB_out:

    def __init__(self, rank):
        os.chdir(HOME + "/project/pyHan/view/static/demo/")
        self.__rdb = redis.StrictRedis(
                host="localhost", port=6388, db=0,
                password="cprt456789", decode_responses=True
        )

        # check rdb control var is exist
        if self.__rdb == None:
            print('Check the database daemon is open!')
            sys.exit(1)

        self.rank = rank
        #self.wdt_conv = {
        #        "uni" : "一字詞",
        #        "bi" : "二字詞",
        #        "tri" : "三字詞",
        #        "four" : "四字詞",
        #        "five" : "五字詞",
        #}
        self.hist_conv = {
            "total_zi" : "統計字數",
            "total_zi_set" : "字集量",
            "total_terms" : "總詞彙量",
            "total_articles" : "總文章量"
        }
        self.history_info = defaultdict(int)
        self.decode = json.JSONDecoder().decode


    """ Optional, omit some words in stats """
    def omit_word(self, freq):
        f = freq
        str_grams = "完整內容請見更多內容請見"
        #conv = {'uni':1, 'bi':2, 'tri':3, 'four':4}
        skip = []
        for N in range(4):
            N += 1
            if N > 1:
                skip += [str_grams[i:i + N] for i in range(len(str_grams) - (N - 1))]

        for ow in skip:
            for pat in f:
                if ow == pat[0]:
                    idx = f.index(pat)
                    f.pop(idx)
        return f


    """ history info fetch and filter
    """

    def get_hist_info(self):
        for k, v in self.__rdb.hgetall('history').items():
            if k == 'total_stats':
                continue
            else:
                key = self.hist_conv[k]
                self.history_info[key] = v


    def get_hist_stats(self):
        stats = self.decode(self.__rdb.hget('history', 'total_stats'))
        return {N: OrderedDict(words) for N, words in stats.items()}


    """ period data fetch and filter """

    def period_faf(self, period):
        stats = self.decode(self.__rdb.hget('snapshot', period))
        return {
                # chinese key    : Oredered hot words (top 10 or whatever)
                #N : OrderedDict(words[:self.rank])
                N : words[:self.rank]  # for website demo which needs sort by freq
                for N, words in stats.items()
        }


    """ dump json file """
    def dump(self, fname, obj):
        with open(fname, 'w') as fp:
            json.dump(obj, fp, ensure_ascii=False, indent=4)


    """ Main work """
    def run(self):
        os.chdir('stats/Ngrams')  # has been changed dir by ../analyze.sh

        period = ('this_year_stats', 'this_month_stats', 'this_week_stats')
        for p in period:
            self.dump(p[:-5]+'hot.json', self.period_faf(p))
            import gc
            gc.collect()


        # histroy data
        self.get_hist_info()
        self.dump('hist_info.json', self.history_info)
        hist_stats = self.get_hist_stats()
        self.dump('total_stats.json', hist_stats)

# End of Pipeout class


if __name__ == "__main__":
    rank = int(sys.argv[1])
    output = DB_out(rank)
    output.run()

# End of file
