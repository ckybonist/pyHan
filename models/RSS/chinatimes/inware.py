#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import json
import urllib
import requests
import feedparser

#from Header.header import *

from info import info
from datetime import datetime
from split_sents import SplitSents
from threading import Thread
from bs4 import BeautifulSoup





def init_fp(url):
    return feedparser.parse(url)


def quote_href(link):
    match = re.search('http:\/\/(.*)', link)
    quoted = urllib.parse.quote(match.group(1))
    return 'http://' + quoted


## Init dir
## invoke by "../get_src.sh then it change dir to models"
#with open("info.json", 'r') as json_file:
#    dirs = list(iload_json(json_file.read()))[0]
#src_dir = dirs['src']['chinatimes']
#rss_dir = dirs['rss_dir']



src_dir = info['src_dir']['chinatimes']
rss_dir = info['rss_dir']


""" It's a class ofinside-ware module to fetch and filter
    RSS item's src then save corpus in local storage.

    @ Save-file: unigrams
    @ EX: ['中', '華', '民', '國', ...]
"""

class Inware:

    def __init__(self):
        self.date = ""
        self.charset = ""
        self.ch_refs = list()


    def filter(self, src):
        pre = str(
            BeautifulSoup(src, "html.parser").findAll('article',{'class': 'clear-fix'}, limit=1))
        post = BeautifulSoup(pre, "html.parser").findAll('p', limit=5)
        return post


    def eval_json(self):
        os.chdir(rss_dir)
        with open('crawler.json', 'r', encoding='utf-8') as json_file:
            self.ch_refs = list(json.load(json_file)['chinatimes']['channels'].values())
        os.chdir(src_dir)


    ''' Naming dir as channel published date '''

    def channelDate(self):
        fp = init_fp('http://www.chinatimes.com/rss/realtimenews-focus.xml').feed.published_parsed
        pubDate = datetime(fp[0], fp[1], fp[2])
        iso_cal = pubDate.isocalendar()

        year = str(pubDate.year)
        month = str(pubDate.month)
        day = str(pubDate.day)
        week = str(iso_cal[1]) 

        return (year, month ,week, day)



    ''' Create dir and save source '''

    def saveData(self, fName, content, href, topic):
        src = {"article" : topic, "href" : href, "content" : content}
        with open(fName, 'w', encoding='utf-8') as json_file:
            json.dump(src, json_file, ensure_ascii=False, indent=4, sort_keys=True)



    """ Get each category's news source and split by punctuation

        Note that some article will lost because of request timeout
    """

    def proc_article(self, fName, target, href, topic):
        sp = SplitSents()
        content = sp.get_sents(target)

        if content is None:
            print('Spliting sentences error for None object')
            sys.exit(1)

        self.saveData(fName, content, href, topic)


    def proc_entries(self, idx):
        entries = init_fp(self.ch_refs[idx]).entries
        (topics, unquoted) = (
            [entry.title for entry in entries], [entry.link for entry in entries])
        entries_ref = [qhf for qhf in map(quote_href, unquoted)]

        for i in range(len(entries_ref)):
            try:
                fName = "ch{0}_e{1}.json".format(str(idx), str(i))
                src = requests.get(entries_ref[i], timeout=4.0)
                src = src.content.decode(src.encoding)
                #src = src.content.decode('utf-8')
                target = self.filter(src)
                if target != []:
                    self.proc_article(fName, target, entries_ref[i], topics[i])
                else:
                    continue

            except KeyboardInterrupt:
                sys._exit(1)

            #except:
                #continue


    def proc_channel(self):
        idx = 0
        while idx < len(self.ch_refs):
            t = Thread(target=self.proc_entries, args=(idx,))
            t.start()
            idx = idx + 1


    def main_work(self, year_dir, mon_dir, week_dir, day_dir):
        '''*Note:
            src_dir-mode in python3 should be 0oxxx,
            else in python2 use 0xxx
        '''
        if not os.path.exists(year_dir):
            src_dir = year_dir + mon_dir + week_dir + day_dir
            os.makedirs(src_dir, 0o711)
            os.chdir(src_dir)
            self.proc_channel()

        elif os.path.exists(year_dir):  # Each week or day work
            os.chdir(year_dir)
            if not os.path.exists(mon_dir):  # Each month work
                src_dir = mon_dir + week_dir + day_dir
                os.makedirs(src_dir, 0o711)
                os.chdir(src_dir)
                self.proc_channel()

            elif os.path.exists(mon_dir):  # Each week or day work
                os.chdir(mon_dir)
                if [week_dir] not in parsed_dirs:
                    src_dir = week_dir + day_dir
                    os.makedirs(src_dir, 0o711)
                    os.chdir(src_dir)
                    self.proc_channel()
                    
                elif [week_dir] in parsed_dirs and \
                     [day_dir] not in parsed_dirs:
                    os.chdir(week_dir)
                    os.mkdir(day_dir, 0o711)
                    os.chdir(day_dir)
                    self.proc_channel()


# End of class




if __name__ == "__main__":
    inw = Inware()
    os.chdir(src_dir)
    
    # define dir name of sources
    parsed_dirs = [d for r, d, f in os.walk(src_dir)] # (r, d, f) eq (root, dirs, files)
    dirs = inw.channelDate()
    dirs = list(map(lambda e: e+'/', dirs))

    inw.eval_json()  # Get the hrefs in json file
    inw.main_work(dirs[0], dirs[1], dirs[2], dirs[3])


# End of Midware.py
