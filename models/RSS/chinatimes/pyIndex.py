#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Parse RSS index title and href, then write to crawler.json

   *Important:
     Because of when sending requst, our URL must be "ascii", but
     sometimes URL will comtain unicode words, so we use regex to get
     string after "http://", then convert it by urllib.parse.quote()
     to get ascii string.

     Finally, combine it( http:// + convert_part), so
     we can't avoid the warning in /LIB/python3.3/http/client.py
'''

import os

HOME = os.environ['HOME']
os.chdir(HOME+"/project/pyHan")

from Header.header import *



with open(HOME+"/project/pyHan/models/init_var.json", 'r') as json_file:
    rss_dir = json.load(json_file)['rss_dir']

os.chdir(rss_dir)

fname = "crawler.json"


class ParseIndexPage():

    def __init__(self):
        self.info = {}  # crawler info
        self.index = ""
        self.channels = list()
        self.article = list()

    def read_info(self):
        with open(fname, 'r') as json_file:
            self.info = json.load(json_file)
        self.index = self.info['chinatimes']['index']

    def init_soup(self):
        http = urllib3.PoolManager(1)
        raw = http.request('GET', self.index).data
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

        channels_block = soup.findAll('div', {'class': 'sitemap-content'})
        a_tags = BeautifulSoup(
            str(channels_block),
            'html.parser').findAll('a',
                                   limit=47)
        chs = [a['href'] for a in a_tags]
        # Channels with quoting if needed
        qchs = [qhref for qhref in map(self.quote_href, chs)]
        for link in qchs:
            ''' Get rss channel title '''
            fp = feedparser.parse(link)
            title = fp.channel.title
            self.article.append(title)

        self.channels = chs

    def __str__(self):
        links = "channels = { "
        for i in range(len(self.channels)):
            links += "\n" + " " * 4 + "u'{0}':'{1}',\n" \
                .format(self.article[i], self.channels[i])
        return links + "\n}\n\n"

    def write_json(self, fName):
        chs = dict(zip(self.article, self.channels))
        value = self.info['chinatimes']
        value.update({'channels' : chs})
        self.info['chinatimes'] = value
        with open(fname, 'w', encoding='utf-8') as json_file:
            json.dump(self.info, json_file, ensure_ascii=False, indent=4, sort_keys=True)

# End of class


if __name__ == "__main__":
    pip = ParseIndexPage()
    pip.read_info()
    pip.find_rss_channels()
    os.chdir(rss_dir)
    pip.write_json("crawler.json")

# End of pyIndex.py
