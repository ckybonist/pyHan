#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

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
    "lexi_dir" : HOME + "/project/pyHan/view/static/demo/lexicon",
    "word_len_max" : 5
}
