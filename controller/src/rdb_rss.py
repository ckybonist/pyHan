#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis

""" Database operation

"""


class Rdb:

    __rdb = None

    def __init__(self):
        self.__rdb = redis.StrictRedis(host="localhost", port=6388, db=0, password="cprt456789")
        self.pipe = self.__rdb.pipeline()


    """ Set hash data """
    def hash_load(self, _hash, _key, _value):
        self.pipe.hset(_hash, _key, _value)


    """ Start pipe """
    def start_pipe(self, flag):
        if flag is 'exec':
            self.pipe.execute()
        else:
            print('Denial of data loading !!!')
        self.pipe.reset()



# End of rdb.py
