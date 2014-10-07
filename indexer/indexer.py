#!/usr/bin/env python

# Vincent de Vos - 24/09/2014 
#
# CHANGELOG
# 0.0.1     Setup initial indexer class

VERSION = (0,0,1)
 
import os
import re
import sys
import operator
import argparse

# http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.punkt.PunktWordTokenizer
from nltk.tokenize.punkt import PunktWordTokenizer

class Indexer:

    """
    The Indexer is responsible for indexing terms and tweets with all extra index-information provided
    """
    
    def __init__(self, mode):
        
        # parse indexer mode
        self.MODES = ('tweets','terms')
        if not mode in self.MODES:
            error("Modus not recognized, try: %s" % ', '.join(self.MODES))
        
        # set default instance variables
        self.MODE = mode
        self.index_meta = {}
        self.index_terms = {}
        self.index_tweets = {}        
    
    def IndexFile(self, fname):
        
        # make sure file exists
        if not os.path.isfile(fname):
            error("Provided file does not exist?")
        
        # read file and itterate over the lines
        with open(fname) as fd:
            content = fd.readlines()

            # index tweets
            if self.MODE == 'tweets':
                for line in content:
                    data = line.strip().split(';')
                    if len(data) >= 2:
                        tweetid = data[0]
                        tweettext = data[1].lower()
                        for term in re.split('[,\s]', tweettext): # PunktWordTokenizer().tokenize(tweettext):
                            if not term == "":
                                self.IndexTerm(term, tweetid)
                
                print "\nExample: get tweets for the term '#yolo'"
                tweets = self.GetTweetsForTerm('#yolo')
                for tweetid in tweets:
                    print " %s" % tweetid
                
                print "\nExample: show occurrence of indexed terms"
                termsbyoccurrence = self.GetIndexedTermsByOccurrence()    
                for term in termsbyoccurrence:
                    print " %s   %s" % (term[1],term[0])
            
            # index terms
            if self.MODE == 'terms':
                for line in [ line.strip() for line in content ]:
                    print line
    
    def ListIndexedTerms(self):
        
        sorted_index_terms = sorted( self.index_terms.items(), key=operator.itemgetter(1), reverse=True)
        for term in sorted_index_terms:
            print term[0]
            for tweetid,val in term[1].iteritems():
                print "  %s (%s)" % (tweetid, val)
    
    def GetTweetsForTerm(self, term):
        
        if term in self.index_terms.keys():
            return self.index_terms[term].keys() 
        return []
            
    def GetIndexedTermsByOccurrence(self):
        
        terms = { }

        for term in self.index_terms.keys():
            terms[term] = self.index_meta[term]['total']
        
        return sorted(terms.items(), key=operator.itemgetter(1), reverse=True)


    # Keep a list of TweetID's for every UT
    def IndexTerm(self, term, tweetid):

        # If the UT has no TweetID's yet first construct a dict for storage
        if not term in self.index_terms.keys():
            self.index_meta[term] = { 'total':0 }
            self.index_terms[term] = { }

        # Just set a TweetID as key with value of 1
        if not tweetid in self.index_terms[term].keys():
            self.index_terms[term][tweetid] = 0
        
        self.index_terms[term][tweetid] += 1
        self.index_meta[term]['total'] += 1
    
    # Return list containing the TweetID's for every Tweet in which the term occurs
    def GetIndexedTerms(self):
        return sorted(self.index_terms)

    def IndexTweet(self, tweetid, tweet):
        pass
 
    
def error(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit()

def main(arguments):
    
    parser = argparse.ArgumentParser(prog="Indexer", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", metavar='file', type=str, nargs='+', help='Input file used for indexing')
    parser.add_argument("--mode",    action='store', default=None, required=True, help="index mode: tweets, terms")
    parser.add_argument("--version", action='store_true', default=False, help="current version")
    args = parser.parse_args(arguments)
    
    if args.version:
        error("Indexer - Version: %d.%d.%d" % VERSION)
    
    indexer = Indexer(args.mode)
    indexer.IndexFile(args.file[0])
    
    """
    indexer.IndexUT('#henk','tweetid_01')
    indexer.IndexUT('#jan' ,'tweetid_02')
    indexer.IndexUT('#henk','tweetid_03')
    indexer.IndexUT('#jan' ,'tweetid_04')
    indexer.IndexUT('#jan' ,'tweetid_05')
    
    for ut in ('#henk','#jan','#piet'):
        print "%s\t%s" % (ut, ', '.join(indexer.GetTweetsForUT(ut)))
    """

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
