#!/bin/sh

# Goal: activate pyindex.py in RSS/$website/ to list index
#       and save record in RSS/crawler.json



PATH=$PATH:/bin:/usr/bin
export PATH


DIR="$HOME/project/pyHan/models/RSS"

for module in $(find $DIR -name 'pyIndex.py' -type f)
do
    python3 $module 2> "/dev/null"
done

