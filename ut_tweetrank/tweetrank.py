#!/usr/bin/env python

# Roy Haanen - 16/10/2014 
#
# CHANGELOG
# 0.0.1     Setup initial tweetrank class

from __future__ import division
from collections import defaultdict

VERSION = (0,0,1)
 
import os
import re
import sys
import json
import math
import pickle
import operator
import argparse

sys.path.insert(0,"../indexer")
from indexer import Indexer

class TweetRank:

    """
    TweetRank takes a file with Unidentified Terms, calculates (using the metrics of a tweet and user as indexed) the top 10 tweet ids ranked for that term and returns this as a list

    """
    
    def __init__(self, args):
        
        self.args = args

        # define noisefilter arguments/parameter input
        self.ACTIONS = ('rank')
        
        # parse noisefilter action
        if not args.action[0] in self.ACTIONS:
            error("Action not recognized, try: %s" % ', '.join(self.ACTIONS))
        self.ACTION = args.action[0]
        
        # instance variables
        self.output_filename = "ut_ranked.txt"
        self.output_filename_clean = "ut_ranked_clean.txt"
        
        self.PerformAction()
    
    def PerformAction(self):
            
        if self.ACTION == 'rank':
            self.TweetRank(self.args.file)
        
    def TweetRank(self, fname):
        
        # make sure file exists
        if not os.path.isfile(fname):
            error("Provided file does not exist?")
        
        # read file and itterate over the lines
        with open(fname) as fd:

            content = fd.readlines()
            unidentified_terms = []
            ranked_tweets = defaultdict(list)
            
            # Create an instance of the indexer
            indexer = Indexer()
            # Index the tweets
            indexer.LoadIndexes()
            
            for line in content:
                
                term = line.strip().split('\t')[0]
                unidentified_terms.append(term)

                # Get the tweets for the read term
                term_tweetids = indexer.GetTweetsForTerm(term)


                # The setup is that the number of retweets, favorites and author followers need to be normalized
                # Normalisation needs maximum and minimum of each of the tweet metrics
                # First loop finds the maximum and minimum value of all metrics. Let's declare them
                max_rt = 0 # will hold max value
                min_rt = 100000 # will hold min value
                max_fav = 0 # will hold max value
                min_fav = 100000 # will hold min value
                max_af = 0 # will hold max value
                min_af = 100000 # will hold min value

                for tweetid in term_tweetids:
                    tweetid_rt = self.GetRetweetsForTweetid(indexer, tweetid)                        
                    if tweetid_rt > max_rt:
                        max_rt = tweetid_rt
                    if tweetid_rt < min_rt:
                        min_rt = tweetid_rt

                    tweetid_fav = self.GetFavsForTweetid(indexer, tweetid)
                    if tweetid_fav > max_fav:
                        max_fav = tweetid_fav
                    if tweetid_fav < min_fav:
                        min_fav = tweetid_fav

                    tweetid_af = self.GetFollowersForTweetid(indexer, tweetid)

                    if tweetid_af > max_af:
                        max_af = tweetid_af
                    if tweetid_af < min_af:
                        min_af = tweetid_af

                # Second loop uses the retrieved max and min of each metric to calculate a normalized score of each tweet for that term 
                for tweetid in term_tweetids:
                    # For every tweet id get the number of retweets, favorites and author followers
                    rt = self.GetRetweetsForTweetid(indexer, tweetid)                        
                    fav = self.GetFavsForTweetid(indexer, tweetid)
                    af = self.GetFollowersForTweetid(indexer, tweetid)
                    
                    tweet_term_score = self.GetScoreForTermTweetid(rt, max_rt, min_rt, fav, max_fav, min_fav, af, max_af, min_af)

                    ranked_tweets[term].append((tweetid,tweet_term_score))

            # Get the rankings, sorted descending on score and return only last x results
            sorted_cropped_rankings = self.SortCropRankings(ranked_tweets, unidentified_terms, 3)
            
            # Write the term with corresponding ranked tweet ids & scores to file    
            with open(self.output_filename, 'w') as outputfile:
                for ut in unidentified_terms:
                    outputfile.write(ut + '\t')
                    number_rankings = len(sorted_cropped_rankings[ut])
                    
                    for i in range(0, number_rankings):
                        outputfile.write(str(sorted_cropped_rankings[ut][i]) + '\t') 
                    
                    outputfile.write('\n')

            # Write the term with corresponding ranked tweet ids CLEAN to file    
            with open(self.output_filename_clean, 'w') as outputfile_clean:
                for ut in unidentified_terms:
                    outputfile_clean.write(ut + '\t')
                    number_rankings = len(sorted_cropped_rankings[ut])
                    
                    for i in range(0, number_rankings):
                        outputfile_clean.write(str(sorted_cropped_rankings[ut][i][0]) + '\t') 
                    
                    outputfile_clean.write('\n')
    
    # Sort the rankings per term and keep only the top x 
    def SortCropRankings(self, ranked_tweets, unidentified_terms, number_to_keep):
        final_rankings = defaultdict(list)

        for term in unidentified_terms:
            # Sort the rankings based on the score
            sorted_rankings = sorted(ranked_tweets[term], key=operator.itemgetter(1), reverse=True)
            
            # Take only the number_to_keep tweets ids, remove the rest
            sorted_cropped_rankings = sorted_rankings[:number_to_keep]

            final_rankings[term] = (sorted_cropped_rankings)
            
        return final_rankings
            

    # GetScoreForTermTweetid normalizes the tweet metrics and returns the sum of the normalized metrics (score) for a tweet, term combination
    def GetScoreForTermTweetid(self, rt, max_rt, min_rt, fav, max_fav, min_fav, af, max_af, min_af):
        weight_rt = 0.4
        weight_fav = 0.2
        weight_af = 0.4


        if (max_rt == min_rt): # catch divide by zero
            norm_rt_score = 0.5
        else:
            norm_rt_score = (rt - min_rt) / (max_rt - min_rt)
        
        if (max_fav == min_fav): # catch divide by zero
            norm_fav_score = 0.5
        else:
            norm_fav_score = (fav - min_fav) / (max_fav - min_fav)
        
        if (max_af == min_af): # catch divide by zero
            norm_af_score = 0.5
        else:
            norm_af_score = (af - min_af) / (max_af - min_af)

        score = round(weight_rt * norm_rt_score + weight_fav * norm_fav_score + weight_af * norm_af_score,2)
        
        return score

    def GetRetweetsForTweetid(self, indexer, tweetid):
        if tweetid in indexer.index_tweets.keys():
            return indexer.index_tweets[tweetid][1]
        return None

    def GetFavsForTweetid(self, indexer, tweetid):
        if tweetid in indexer.index_tweets.keys():
            return indexer.index_tweets[tweetid][2]
        return None

    def GetFollowersForTweetid(self, indexer, tweetid):
        if tweetid in indexer.index_tweets.keys():
            return indexer.index_tweets[tweetid][3]
        return None

def error(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit()

def main(arguments):
    
    parser = argparse.ArgumentParser(prog="TweetRank", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", metavar='action', type=str, nargs='+', help='Action for NoiseFilter: filter')
    parser.add_argument("--file", metavar='file', type=str, help='Input file used for ranking actions')
    parser.add_argument("--version", action='store_true', default=False, help="current version")
    args = parser.parse_args(arguments)
    
    if args.version:
        error("TweetRank - Version: %d.%d.%d" % VERSION)
    
    tweetrank = TweetRank(args)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
