#!/bin/sh
# Goal: activate inware.py in RSS/$website/ to get sources(json file)


PATH="/bin:/usr/bin"
export PATH

DIR="$HOME/project/pyHan/models/RSS"

# Use for each web-page's inward.py loading init var of directory 
MODELS="$HOME/project/pyHan/models/"

for module in $(find $DIR -name 'inware.py' -type f)
do
    cd $MODELS
    #python3 $module 2> "/dev/null"
    python3 $module 2> err.txt
done

