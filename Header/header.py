#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import json
import urllib
import urllib3
import requests
import feedparser
from functools import reduce
from threading import Thread
from datetime import datetime
from bs4 import BeautifulSoup
from collections import Counter, defaultdict


HOME = os.environ['HOME']
info = {
    "src_dir":{
        "root" : HOME + "/project/sources",
        "chinatimes" : HOME + "/project/sources/chinatimes",
        "yahoo" : HOME + "/project/sources/yahoo",
        "udn" : HOME + "/project/sources/udn",
        "nowNews" : HOME + "/project/sources/now_news"
    },
    "rss_dir" : HOME + "/project/pyHan/models/RSS",
    "lexi_dir" : HOME + "/project/pyHan/res/lexicon",
    "word_len_max" : 5
}



# Functions Group
def iload_json(buff, decoder=None, _w=json.decoder.WHITESPACE.match):
    """ Generate a sequence of top-level JSON values
        declared in the buffer.

        EX: list(iload_json('[1, 2] "a" { "c": 3 }'))
        [[1, 2], u'a', {u'c': 3}]}'))
    """
    decoder = decoder or json._default_decoder
    idx = _w(buff, 0).end()
    end = len(buff)

    try:
        while idx != end:
            (val, idx) = decoder.raw_decode(buff, idx=idx)
            yield val
            idx = _w(buff, idx).end()
    except ValueError as exc:
        raise ValueError('%s (%r at position %d).' % (exc, buff[idx:], idx))


def init_fp(link):
    return feedparser.parse(link)


def add(x, y):
    return x+y


def quote_href(link):
    match = re.search('http:\/\/(.*)', link)
    quoted = urllib.parse.quote(match.group(1))
    return 'http://' + quoted


def get_han(string):
    result = [s for s in re.findall(u"[\u4e00-\u9fa5]+", string) if s != ""]
    result = reduce(lambda e1,e2: e1+e2, result, "")
    return result




class SplitSents:
    def __init__(self):
        self.cut_symbol = "，。？！：;,.?!；、"
        pass

    def FindToken(self, cutlist, char):
        if char in cutlist:
            return True
        else:
            return False


    def split_sents(self, lines):
        cutlist = list(self.cut_symbol)
        be_splited = []
        tmp = []

        for ln in lines:
            if self.FindToken(cutlist, ln):
                tmp.append(ln)
                be_splited.append(''.join(tmp))
                tmp = []
            else:
                tmp.append(ln)
        yield be_splited
        #return be_splited


    def get_sents(self, target_tags):
        result = []
        for tag in target_tags:
            iter_sents = self.split_sents(str(tag))
            splited_sents = [
                    get_han(str(s))
                    for sents in iter_sents for s in sents
                    if get_han(str(s)) != ""
            ]
            result += splited_sents
        return result


class Segwords:
    def __init__(self, _min, _max):
        self.wdl_min = _min
        self.wdl_max = _max
        self.wdt_conv = {  # wdt -> word type
             0 : 'uni',
             1 : 'bi',
             2 : 'tri',
             3 : 'four',
             4 : 'five',
        }

    def n_grams(self, sentences, N):
        for sent in sentences:
            gen = range(len(sent) - (N-1))
            for i in gen:
                yield sent[i:i+N]
        #yield [sent[i:i + N] for i in gen]


    def seg_words(self, sentences):
        mmw = defaultdict(list)

        try:
            with open(self.lexi_dir + '/Ngrams.json') as json_file:
                lexicon = json.load(json_file)
        except IOError:
            print('N-grams lexicon not found, process exit...')
            sys.exit(1)

        def match(word, word_type):
            if word in lexicon[str(word_type)]:
                return True
            else:
                return False

        for s in sentences:
            while(s != ''):
                longest = s[:self.wdl_max]
                if match(longest, self.wdl_max-1) is True:
                    mmw[self.wdt_conv[self.wdl_max-1]].append(longest)
                    #self.mmw[self.wdt_conv[self.wdl_max-1]].append(longest)
                    s = s[self.wdl_max:]
                else:
                    for j in reversed(range(1, self.wdl_max)):
                        sub_str = longest[0:j]
                        if j > 1 and match(sub_str, j) is True:
                            mmw[self.wdt_conv[j-1]].append(sub_str)
                            #self.mmw[self.wdt_conv[j-1]].append(sub_str)
                            s = s[j:]
                            break
                        elif j==1:
                            s = s[j:]
                            break
        return mmw


class Cnt:

    def __init__(self):
        pass

    # count grams frequence
    def count_freq(self, words, rank):
        return Counter(words).most_common(rank)

# End of Class Cnt




### TODO

# End of header.py
