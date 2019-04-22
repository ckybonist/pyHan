#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Parse UDN RSS index title and href, then write to crawler.json

   *Important:
     Because of when sending requst, our URL must be "ascii", but
     sometimes URL will comtain unicode words, so we use regex to get
     string after "http://", then convert it by urllib.parse.quote()
     to get ascii string.

     Finally, combine it( http:// + convert_part), so
     we can't avoid the warning in /LIB/python3.3/http/client.py
'''

import os
import info as myinfo


HOME = os.environ['HOME']
os.chdir(HOME+"/project/pyHan")

from Header.header import *


rss_dir = myinfo.info['rss_dir']

os.chdir(rss_dir)



class ParseIndexPage():

    def __init__(self):
        self.info = {}  # crawler info
        self.index = ""
        self.channels = list()
        self.article = list()


    def read_info(self):
        with open('crawler.json', 'r') as json_file:
            self.info = json.load(json_file)
        self.index = self.info['udn']['index']


    def init_soup(self):
        raw = requests.get(self.index).content.decode('big5')
        return BeautifulSoup(raw, 'html.parser')


    def quote_href(self, link):
        # Rule to grep news category
        match = re.search('http:\/\/(\S+)', link)
        link = 'http://' + urllib.parse.quote(match.group(1))
        return link


    def find_rss_channels(self):
        soup = self.init_soup()
        if soup is None:
            print('Connection Error! Cannot fetch web page content')

        pre_soup = soup.findAll('td', {'class': 'subcategory_topic'})
        chs_hrefs = [tag['href'] for tag in BeautifulSoup(str(pre_soup), "html.parser").findAll('a')]

        # Channels with quoting if needed
        #qchs = [qhref for qhref in map(self.quote_href, chs)]

        self.article = [feedparser.parse(link).channel.title for link in chs_hrefs \
                              if 'title' in feedparser.parse(link).channel.keys()] 
        self.channels = chs_hrefs


    def __str__(self):
        links = "channels = { "
        for i in range(len(self.channels)):
            links += "\n" + " " * 4 + "u'{0}':'{1}',\n" \
                .format(self.article[i], self.channels[i])
        return links + "\n}\n\n"


    def write_json(self, fName):
        chs = dict(zip(self.article, self.channels))
        value = self.info['udn']
        value.update({'channels' : chs})
        self.info['udn'] = value
        with open(fName, 'w', encoding='utf-8') as json_file:
            json.dump(self.info, json_file, ensure_ascii=False, indent=4, sort_keys=True) 
# End of class


if __name__ == "__main__":
    pip = ParseIndexPage()
    pip.read_info()
    pip.find_rss_channels()
    os.chdir(rss_dir)
    pip.write_json('crawler.json')

# End of pyIndex.py
