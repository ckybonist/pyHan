#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import json
import redis
from collections import defaultdict
from collections import OrderedDict
from abc import ABCMeta, abstractmethod



""" Meta Class of Lexicon

    Firstly, get N-grams and Maximum-Matching stats from "DB".
    Secondly, filter and extract stats to lexicon

    Filter method:
        - get diff rate(%) between two words and divide adjancent
          diff rate(w[i] / w[j], which j > i), if result > 0, then
          slice stats => stats[:i]

        - K-means algorithm to analyze stats cluster

    Lexicon type:
        N-Grams
        MM (Maximum Matching)
"""

class Lexicon(metaclass = ABCMeta):
    def __init__(self, th):
        os.chdir(os.environ['HOME'] + "/project/pyHan/view/static/demo/")
        self.threshold = th
        self.wtp_conv = {
                    "uni" : 1,
                    "bi" : 2,
                    "tri" : 3,
                    "four" : 4,
                    "five" : 5
                }
        self.stats = {}
        self.lexicon = {}


    @abstractmethod
    def get_stats(self):
        pass


    def get_percent(self, mole, denomi, precision):
        return round(100 * (mole/denomi), precision)


    def gen_lexicon(self):
        conv = self.wtp_conv
        get_percent = self.get_percent
        for wdt, grams in self.stats.items():  # grams : (word : frequence)

            if wdt == 'uni':  # target is to generate word lexicon
                continue
            else:
                for i in range(len(grams) - 2):
                    pre_dr = get_percent(
                            abs(grams[i][1] - grams[i+1][1]),
                            max(grams[i][1], grams[i+1][1]),
                            2
                    )  # dr -> diff rate
                    post_dr = get_percent(
                            abs(grams[i+1][1] - grams[i+2][1]),
                            max(grams[i+1][1], grams[i+2][1]),
                            2
                    )
                    if pre_dr > 0 and post_dr > 0:
                        final_dr = get_percent(
                                abs(pre_dr - post_dr),
                                (pre_dr + post_dr)/2,
                                #post_dr,
                                #pre_dr,
                                #max(pre_dr, post_dr),
                                2
                        )
                        if final_dr > self.threshold[wdt]:
                            if pre_dr > post_dr:
                                lexi_N = grams[:i]
                                #lexi_N = OrderedDict(grams[:i])
                            elif pre_dr < post_dr:
                                lexi_N = grams[:i+1]
                                #lexi_N = OrderedDict(grams[:i+1])
                            self.lexicon.update({wdt : lexi_N})
                        else:
                            continue


    def write_out(self):
        os.chdir('lexicon')  # has been changed dir by ../analyze.sh
        #os.chdir("../res/lexicon")

        def dump(fname, obj):
            with open(fname, 'w') as fp:
                json.dump(obj, fp, ensure_ascii=False, indent=4)

        fname = self.__class__.__name__ + '.json'
        dump(fname, self.lexicon)

    @abstractmethod
    def run(self):
        pass

# End of ABC Lexicon



class Ngrams(Lexicon):
    def __init__(self, th):
        super(Ngrams, self).__init__(th)
        self.__rdb = redis.StrictRedis(
                host="localhost", port=6388,
                db=0, password="cprt456789",
                decode_responses=True
        )


    def get_stats(self):
        if self.__rdb == None:
            print('Check the database daemon is open!')
            sys.exit(1)

        decode = json.JSONDecoder().decode
        self.stats = decode(self.__rdb.hget('history', 'total_stats'))


    def run(self):
        self.get_stats()
        super(Ngrams, self).gen_lexicon()
        super(Ngrams, self).write_out()

# End of Class Ngrams



class MM(Lexicon):
    def __init__(self, th):
        super(MM, self).__init__(th)
        self.__rdb = redis.StrictRedis(
                host="localhost", port=6388,
                db=0, password="cprt456789",
                decode_responses=True
        )


    def get_stats(self):
        if self.__rdb == None:
            print('Check the database daemon is open!')
            sys.exit(1)

        decode = json.JSONDecoder().decode
        self.stats = decode(self.__rdb.hget('MM', 'stats'))


    def run(self):
        self.get_stats()
        super(MM, self).gen_lexicon()
        super(MM, self).write_out()

# End of Class MM



if __name__=="__main__":
    TYPE = sys.argv[1]

    th = {"bi":5, "tri":0.5, "four":0.5, "five":0.5}  # percentage threshold to extract raw stats to lexicon

    # init object type
    if TYPE == 'N-grams':
        analyze = Ngrams(th)
    elif TYPE == 'MM':
        analyze = MM(th)
    else:
        print('Input correct argv (N-grams or MM)')
        sys.exit(1)

    analyze.run()

# End of lexicon.py
