#!/bin/sh
# 
# Analyze chinese text source and split each word
# by using N-grams or Maximum Matching and count 
# frequence of every word
#
# After upon process, saving result to DB
# and write stats and lexicon to local storage
#
# Note that this script will handle all py module's
# dir changing status



# Init

PATH="$PATH:/bin:/usr/bin"
SRC="$HOME/project/pyHan/controller/src"
RESOURCES="$HOME/project/pyHan/view/static/demo"

export PATH


# analyze type

TYPE=$1  


# range of hot words ranking

RANK=$2



# Check argv[1] (N-grams or MM)

test $TYPE != "N-grams" && test $TYPE != "MM" && \
    echo 'Input analyze type: N-grams or MM (maximum matching)' && exit 1


# Check argv[2] is number

ISNUM='^[0-9]+$'

if ! [[ $RANK =~ $ISNUM ]] && [ $TYPE == "N-grams" ]; then
    echo 'Second argv must be a number'; exit 1
fi



# Check redis-server is open
# change username to fit yous, in my case: kwanyu

test -z "`ps aux | grep -v grep | grep jm1592 | grep redis-server`" && \
echo 'redis-server is not open' && exit 1



# Check resources dir

if [ ! -d "$RESOURCES/stats/N-grams" ] && [ ! -d "$RESOURCES/lexicon" ]; then
    echo 'Resource dir not found, please create it' && exit 1
fi


# Start analyzing

cd $SRC

if [ -f "words_stats.py" ]; then

    python3 words_stats.py $TYPE
fi


if [ $TYPE == "N-grams" ] && [ -f "fetch_stats.py" ]; then

    # N-grams stats
    python3 fetch_stats.py $RANK
fi


if [ -f "lexicon.py" ]; then
    python3 lexicon.py $TYPE
fi


# End of analyze.sh
