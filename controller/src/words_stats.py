#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gc
import re
import sys
import json

# Database
from rdb_rss import Rdb

# load info
from info import info

# Get current time
from datetime import datetime

# for meta class
from abc import ABCMeta, abstractmethod
from collections import Counter, defaultdict

# Do not use if you want to
# run module in crontab
# Load own funcs
#from Header.header import *


""" Abstract class of segementation and collect statistics

    @TYPE: N-grams, Maximum Matching
"""
class Analyze(metaclass=ABCMeta):
    def __init__(self):
        #self.cnt = Cnt()
        self.wdt_conv = {  # wdt -> word type
             0 : 'uni',
             1 : 'bi',
             2 : 'tri',
             3 : 'four',
             4 : 'five',
        }
        self.meta_keys = ['total', 'y', 'm', 'w']  # meta keys of time period
        self.src_dir = info['src_dir']['root']
        self.lexi_dir = info['lexi_dir']
        self.wdl_max = info['word_len_max']
        self.wdl_min = 0


    def encode_obj(self, obj):
        json_encode = json.JSONEncoder(ensure_ascii=False, sort_keys=True).encode
        return json_encode(obj)


    # count grams frequence and sort by rank
    def count_freq(self, words, rank):
        return Counter(words).most_common(rank)


    """ Gather all sources abs path to one list,
        finally, return it
    """
    def walk_src_path(self):
        import fnmatch  # filter path
        sources = []
        for root, dirnames, filenames in os.walk(self.src_dir):
            for fname in fnmatch.filter(filenames, '*.json'):
                fullpath = os.path.join(root, fname)
                if os.path.exists(fullpath):
                    sources.append(fullpath)
        return sources


    @abstractmethod
    def gather_sentences(self, period=None):
        pass

    @abstractmethod
    def seg_words(self):
        pass

    @abstractmethod
    def collect_freq(self, period=None):
        pass

    @abstractmethod
    def run(self):
        pass

# End of ABC Analyze


### Fix this class to inherite Analyze ABC
""" N-grams method to split text to words and collect different
    time period(total, year, month, week) stats, finally, load
    the stats and relative info to DB.

    Note: Keys (y, m, w)  indicates (this_year, this_month, this_week)
"""
class Ngrams(Analyze):

    def __init__(self, omit):
        super(Ngrams, self).__init__()
        self.stats = defaultdict(dict)
        self.a_info = defaultdict(int)  # analyze info
        self.omit = omit


    """ Collecting different time period's multigrams statistics and info

    """
    def gather_sentences(self, period):
        # Use for merge list element
        from itertools import chain

        if not period in self.meta_keys:  # check argv
            print('key error (period)')
            sys.exit(1)

        # get current time
        now = datetime.now()
        week = datetime.isocalendar(now)[1]
        now = (str(now.year), str(now.month), str(week))

        sents_of_period = []

        sources = super(Ngrams, self).walk_src_path()

        self.a_info['total_articles'] = len(sources)

        # seperate path name by slash rule
        # sep_pn => ".*/website/year/month/week/day/.*"
        sep_pn = re.compile('.*/(\S+)/(\S+)/(\S+)/(\S+)/(\S+)/.*')

        # gather sentences
        for src in sources:
            with open(src, mode='r', encoding='UTF-8') as jf:
                sentences = json.load(jf)['content']
            if not sentences:
                continue
            else:
                pop = sep_pn.findall(src)[0]  # part of path
                if period == 'total':
                    self.a_info['total_zi'] += len(list(chain(*sentences)))
                    sents_of_period += sentences

                elif period == 'y':
                    if pop[1] == now[0]:
                        sents_of_period += sentences

                elif period == 'm':
                    if pop[2] == now[1]:
                        sents_of_period += sentences

                elif period == 'w':
                    if pop[3] == now[2]:
                        sents_of_period += sentences
                else:
                    return []  # default is return blank list

        gc.collect()
        #print('gargabe collected')
        #print('gather sentences complete for period {0}'.format(period))
        return sents_of_period
    # End of function


    """ Split word by N-Grams method """
    def seg_words(self, sentences, N):
        for sent in sentences:
            gen = range(len(sent) - (N-1))
            for i in gen:
                yield sent[i:i+N]
        #split = self.cnt.n_grams
        #return split(sentences, N)


    """ Filter some words with really high frequence

        Add omitted words in list omit
    """
    def filter(self, stats, N):
        seg_omit = defaultdict(dict)
        conv = self.wdt_conv

        # generate omitted N-grams
        for n in range(self.wdl_min, self.wdl_max):
            seg_omit[conv[n]] = [w for w in self.seg_words(self.omit, n+1)]

        # filter
        if N == 0:
            pass
        else:
            for w in seg_omit[N]:
                for tup in stats[N]:
                    if w == tup[0]:
                        idx = stats[N].index(tup)
                        stats[N].pop(idx)
        return stats


    """ Function of word frequence statistics """
    def collect_freq(self, period):
        stats = defaultdict(dict)
        count = super(Ngrams, self).count_freq
        conv = self.wdt_conv

        # Testing Code (reduce memory exhaust)
        # =========================================================
        raw = self.gather_sentences(period=period)

        if raw:
            for n in range(self.wdl_min, self.wdl_max):
                N = conv[n]
                words = [w for w in self.seg_words(raw, n+1)]
                stats[N] = count(
                        #[w for w in self.seg_words(raw, N+1)],
                        words,  # period words which has been splited
                        None
                )
                stats = self.filter(stats, N)  # filter some words probably have extreme frequence

            if period == 'total':
                self.a_info['total_zi_set'] = len(stats['uni'])
                for freq_pair in stats.values():
                    self.a_info['total_terms'] += len(freq_pair)
        # ========================================================
        del raw
        gc.collect()
        #print('gargabe collected')
        #print('{0} freq collecting complete\n\n\n'.format(period))
        return stats


    """ Function of loading data to Database """

    def run(self):
        rdb = Rdb()
        encode = self.encode_obj

        # statistics
        rdb.hash_load('history', 'total_stats', encode(self.collect_freq('total')))
        rdb.hash_load('snapshot', 'this_year_stats', encode(self.collect_freq('y')))
        rdb.hash_load('snapshot', 'this_month_stats', encode(self.collect_freq('m')))
        rdb.hash_load('snapshot', 'this_week_stats', encode(self.collect_freq('w')))

        # info
        rdb.hash_load('history', 'total_zi', self.a_info['total_zi'])
        rdb.hash_load('history', 'total_zi_set', self.a_info['total_zi_set'])
        rdb.hash_load('history', 'total_terms', self.a_info['total_terms'])
        rdb.hash_load('history', 'total_articles', self.a_info['total_articles'])

        rdb.start_pipe('exec')

# End of Class Ngrams



""" Using Maximum Matching algorithm to split text to words
    and collect its stats, finally, load the stats and relative
    info to DB.

"""

class MM(Analyze):
    def __init__(self):
        super(MM, self).__init__()
        self.stats = defaultdict(dict)


    def gather_sentences(self):
        sources = super(MM, self).walk_src_path()
        sentences = []
        for src in sources:
            with open(src, mode='r', encoding='UTF-8') as jf:
                content = json.load(jf)['content']
            if not content:
                continue
            else:
                sentences += content
        return sentences


    """ Maximum Matching algorithm for word segment """
    def seg_words(self, sentences):
        mmw = defaultdict(list)

        try:
            with open(self.lexi_dir + '/Ngrams.json') as json_file:
                from collections import OrderedDict
                lexicon = json.load(json_file)

                for n, grams in lexicon.items():
                    lexicon[n] = OrderedDict(grams)
        except IOError:
            print('N-grams lexicon not found, process exit...')
            sys.exit(1)


        def match(word, word_type):
            if word in lexicon[self.wdt_conv[word_type]]:
                return True
            else:
                return False


        for s in sentences:
            while(s != ''):
                longest_word = s[:self.wdl_max]
                if match(longest_word, self.wdl_max-1) is True:
                    key = self.wdt_conv[self.wdl_max-1]

                    mmw[key].append(longest_word)

                    s = s[self.wdl_max:]
                else:
                    for j in reversed(range(1, self.wdl_max)):
                        sub_str = longest_word[0:j]

                        if j > 1 and match(sub_str, j-1) is True:
                            key = self.wdt_conv[j-1]
                            mmw[key].append(sub_str)
                            s = s[j:]
                            break
                        elif j==1:
                            s = s[j:]
                            break
        return mmw


    def gather_words(self):
        sentences = self.gather_sentences()
        words = self.seg_words(sentences)
        return words


    def get_freq(self, mgs):
        count = super(MM, self).count_freq
        return {wdt:count(words, None) for wdt, words in mgs.items()}


    def collect_freq(self):
        self.stats = self.get_freq(self.gather_words())


    def run(self):
        # Collecting words frequences
        self.collect_freq()

        # Load data to DB
        rdb = Rdb()
        stats = super(MM, self).encode_obj(self.stats)

        rdb.hash_load('MM', 'stats', stats)
        rdb.start_pipe('exec')

# End of Class MM



if __name__ == "__main__":

    TYPE = sys.argv[1]  # Type of analyze

    # words list you want to omit in N-grams, add it by yourself
    omit = [
        "中央社記者",
        "新聞相關影音",
        "自由時報記者",
        "至明年月日起"
    ]

    # init object type
    if TYPE == 'MM':
        analyze = MM()
    elif TYPE == 'N-grams':
        analyze = Ngrams(omit)
    else:
        print('Error occurred! Check argv is N-grams or MM')
        sys.exit(1)

    analyze.run()

# End of filter.py
