#!/usr/bin/env python

# Vincent de Vos - 24/09/2014 
#
# CHANGELOG
# 0.0.1     Setup initial indexer class

VERSION = (0,0,1)
 
import os
import sys
import argparse

class Indexer:

    """
    The Indexer is responsible for indexing terms and tweets with all extra index-information provided
    """
    
    def __init__(self):

        self.index_uts = {}
        self.index_tweets = {}        

    # Keep a list of TweetID's for every UT
    def IndexUT(self, ut, tweetid):

        # If the UT has no TweetID's yet first construct a dict for storage
        if not ut in self.index_uts.keys():
            self.index_uts[ut] = {}

        # Just set a TweetID as key with value of 1
        self.index_uts[ut][tweetid] = 1
    
    # Return list containing the TweetID's for every Tweet in which the UT occurs
    def GetTweetsForUT(self, ut):

        # If the UT exists in the index return all the TweetID's
        if ut in self.index_uts.keys():
            return sorted(self.index_uts[ut].keys())

        # If UT not exists return empty list
        return []

    def IndexTweet(self, tweetid, tweet):
        pass
 
    
def error(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit()

def main(arguments):
    
    parser = argparse.ArgumentParser(prog="Indexer", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode",    action='store', default=None, required=True, help="index mode: tweets, terms")
    parser.add_argument("--version", action='store_true', default=False, help="current version")
    args = parser.parse_args(arguments)
    
    if args.version:
        error("Indexer - Version: %d.%d.%d" % VERSION)
    
    modes = ('tweets','terms')
    if not args.mode in modes:
        error("Modus not recognized, try: %s" % ', '.join(modes))

    indexer = Indexer()
    indexer.IndexUT('#henk','tweetid_01')
    indexer.IndexUT('#jan' ,'tweetid_02')
    indexer.IndexUT('#henk','tweetid_03')
    indexer.IndexUT('#jan' ,'tweetid_04')
    indexer.IndexUT('#jan' ,'tweetid_05')
    
    for ut in ('#henk','#jan','#piet'):
        print "%s\t%s" % (ut, ', '.join(indexer.GetTweetsForUT(ut)))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
