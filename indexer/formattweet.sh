#!/bin/sh

# By: Vincent de Vos
# Usage: formattweets.sh [tweetfile] > outfile
#
# @Input: CSV file containing tweets
# @Output: Cleaned and tab seperated tweet file for the indexer

cat $1 \
    | awk -F',' '{ if(NF == 5) { print $0; } }' \
    | sed 's///g' \
    | sed 's/"//g' \
    | awk -F',' '{ print $1"   "$4"    "$5"    "$3"    "$2; }' \
    | grep -iP "^[0-9]+" \
    | sort -u 
