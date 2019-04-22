#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from functools import reduce



class SplitSents:
    def __init__(self):
        self.cut_symbol = "，。？！：;,.?!；、"
        pass

    def FindToken(self, cutlist, char):
        if char in cutlist:
            return True
        else:
            return False


    def get_han(self, string):
        result = [s for s in re.findall(u"[\u4e00-\u9fa5]+", string) if s != ""]
        result = reduce(lambda e1,e2: e1+e2, result, "")
        return result


    def split_sents(self, lines):
        cutlist = list(self.cut_symbol)
        be_splited = []
        tmp = []

        for ln in lines:
            if self.FindToken(cutlist, ln) or lines[-1:] == ln:
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
                    self.get_han(str(s))
                    for sents in iter_sents for s in sents
                    if self.get_han(str(s)) != "" 
            ]
            result += splited_sents
        return result


# End of split_sents.py
