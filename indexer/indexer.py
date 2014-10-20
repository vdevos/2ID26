#!/usr/bin/env python

# Vincent de Vos - 24/09/2014 
#
# CHANGELOG
# 0.0.1     Setup initial indexer class

VERSION = (0, 0, 1)

import os
import re
import sys
import json
import math
import pickle
import operator
import argparse

# http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.punkt.PunktWordTokenizer
from nltk.corpus import stopwords


class Indexer:
    """
    The Indexer is responsible for indexing terms and tweets with all extra index-information provided
    """

    def __init__(self):

        # instance variables
        self.index_tf = {}
        self.index_idf = {}
        self.index_terms = {}
        self.index_matrix = {}
        self.index_tweets = {}

    def StoreIndexes(self):
        # for every index we keep, we write a pickled file to disk
        pickle.Pickler(open("index_tf.index", "wb"), protocol=2).dump(self.index_tf)
        pickle.Pickler(open("index_idf.index", "wb"), protocol=2).dump(self.index_idf)
        pickle.Pickler(open("index_matrix.index", "wb"), protocol=2).dump(self.index_matrix)
        pickle.Pickler(open("index_terms.index", "wb"), protocol=2).dump(self.index_terms)
        pickle.Pickler(open("index_tweets.index", "wb"), protocol=2).dump(self.index_tweets)

    def LoadIndexes(self):

        # try to load stored indexes from disk
        if os.path.isfile('index_idf.index'):
            self.index_idf = pickle.Unpickler(open("index_idf.index", "rb"), fix_imports=True, encoding="UTF-8").load()
        if os.path.isfile('index_tf.index'):
            self.index_tf = pickle.Unpickler(open("index_tf.index", "rb"), fix_imports=True, encoding="UTF-8").load()
        if os.path.isfile('index_matrix.index'):
            self.index_matrix = pickle.Unpickler(open("index_matrix.index", "rb"), fix_imports=True, encoding="UTF-8").load()
        if os.path.isfile('index_terms.index'):
            self.index_terms = pickle.Unpickler(open("index_terms.index", "rb"), fix_imports=True, encoding="UTF-8").load()
        if os.path.isfile('index_tweets.index'):
            self.index_tweets = pickle.Unpickler(open("index_tweets.index", "rb"), fix_imports=True, encoding="UTF-8").load()

    def Tokenize(self, text):
        words = []
        for term in re.split('[,\s]', text):
            if len(term) > 1 and not term.decode('utf-8') in stopwords.words('english'):
                words.append(term)
        return words


    def IndexFile(self, fname):

        # make sure file exists
        if not os.path.isfile(fname):
            error("Provided file does not exist?")

        # read file and iterate over the lines
        with open(fname) as fd:

            content = fd.readlines()

            for line in content:

                data = line.strip().split('\t')

                if len(data) >= 6:

                    tweetid = data[0]
                    tweetrt = int(data[1])
                    tweetfav = int(data[2])
                    tweetaf = int(data[3])
                    tweetauthor = data[4]
                    tweettext = self.Tokenize(data[5].lower())

                    for t1 in tweettext:

                        # Construct a 2-dimensional matrix holding term-by-term frequency
                        # (how many times did a term occur in a tweet together with a other term)
                        if not t1 in self.index_matrix.keys():
                            self.index_matrix[t1] = {}

                        for t2 in tweettext:
                            if not t2 in self.index_matrix[t1].keys():
                                self.index_matrix[t1][t2] = 0

                        # Construct a index that contains all the tweetid's each time a term occurs in a tweet
                        self.IndexTerm(t1, tweetid)

                        # Construct a index that tracks term-by-term frequence
                        self.IndexTermByTermFrequency(t1, tweettext)

                    # Construct a index that stores tweets by their tweetid               
                    self.IndexTweet(tweetid, tweettext, tweetrt, tweetfav, tweetaf, tweetauthor)

        self.StoreIndexes()

    def List(self):

        print("\nExample: show top 5 indexed terms sorted by occurrence (descending) and the tweets(id) they occur in")
        termsbyoccurrence = self.GetTermsByOccurrence()
        for term in termsbyoccurrence[0:5]:
            print("%s  %s" % (term[1], term[0]))
            self.GetTweetsForTerm(term[0], withFrequency=True)

        print("\nExample: for the top 5 indexed terms show a top 5 of words that often occurred together")
        for term in termsbyoccurrence[0:5]:
            print("%s  %s" % (term[1], term[0]))
            terms = self.GetTermsForTerm(term[0])
            for cterm in terms[0:5]:
                print("  %s (%s)" % (cterm[0], cterm[1]))

                # print indexed data
                # for tweetid, tweettext in self.index_tweets.iteritems():
                #    print "%s   %s" % (tweetid, tweettext)

    def ClusterTerms(self, term=None):

        # Using Euclidean distance (http://en.wikipedia.org/wiki/Euclidean_distance) for simple 'clustering' 
        # ED = Euclidean Distance
        # Every term can be represented as a vector in N-space using a vector V = [T1, T2, ..., Tn] 
        # The values within this vector represent the frequency of the 'main' term with the other terms
        # (each time that other term occurs within a same tweet)

        # These frequency values are used to calculate the Euclidean distance to every other term in our vector space
        # (except the 'main' term itself)
        # In the end we end up with a list of terms and a ED-score with respect to the input term
        # Ignore ED with score 0. Matching: 0 < EDS

        scores = {}

        for row in self.index_matrix.keys():
            if not term == row:
                ed = 0  # Euclidean distance
                for term1, value1 in self.index_matrix[term].iteritems():
                    td = 0  # Term delta
                    if term1 in self.index_matrix[row]:
                        td = value1 - self.index_matrix[row][term1]
                    ed += math.pow(td, 2)
                ed = math.floor(math.sqrt(ed))
                scores[row] = ed

        scores = sorted(scores.items(), key=operator.itemgetter(1))
        count = 0
        for score in scores:
            if score[1] > 0:
                print("%s (%s)" % (score[0], score[1]))
                count += 1
            if count == 25:
                break

    def GetTweetsForTerm(self, term, withFrequency=False):

        if term in self.index_terms.keys():
            if not withFrequency:
                return self.index_terms[term].keys()
            else:
                return self.index_terms[term]
        return []

    def GetIDFForTerm(self, term):

        # Calculate TF*IDF for a term
        # http://en.wikipedia.org/wiki/Tf-idf

        idf = 0.00
        doccount = float(len(self.index_tweets))

        if term in self.index_terms.keys():
            ndt = float(len(self.index_terms[term].keys()))
            idf = math.log(doccount / ndt)

        return round(idf, 2)

    def GetTFIDFForTerm(self, term, tweetid):

        tf = 0
        document = self.GetTweetForTweetid(tweetid, tokenized=True)
        if document:
            for t in document:
<<<<<<< HEAD
                print(t)
=======
>>>>>>> FETCH_HEAD
                if t == term:
                    tf += 1

        idf = self.GetIDFForTerm(term)

        return tf * idf


    def GetTermsByOccurrence(self):

        return sorted(self.index_tf.items(), key=operator.itemgetter(1), reverse=True)


    # Keep a list of TweetID's for every UT
    def IndexTerm(self, term, tweetid):

        # If the term has no TweetID's yet first construct a dict for storage
        if not term in self.index_terms.keys():
            self.index_terms[term] = {}

        # Just set a TweetID as key with value of 1
        if not tweetid in self.index_terms[term].keys():
            self.index_terms[term][tweetid] = 0

        # Set initial TF
        if not term in self.index_tf.keys():
            self.index_tf[term] = 0

        # Update frequencies
        self.index_tf[term] += 1
        self.index_terms[term][tweetid] += 1

    def GetTermsForTerm(self, term):

        if term in self.index_matrix:
            return sorted(self.index_matrix[term].items(), key=operator.itemgetter(1), reverse=True)
        return []

    def IndexTermByTermFrequency(self, term, tweettext):

        for tterm in tweettext:
            self.index_matrix[term][tterm] += 1

    def IndexTweet(self, tweetid, tweettext, tweetrt, tweetfav, tweetaf, tweetauthor):
        self.index_tweets[tweetid] = (tweettext, tweetrt, tweetfav, tweetaf, tweetauthor)

    def GetTweetForTweetid(self, tweetid, tokenized=False):
        if tweetid in self.index_tweets.keys():
            if tokenized:
                return self.index_tweets[tweetid][0]
            else:
                return ' '.join(self.index_tweets[tweetid][0])
        return None


def djson(data):
    print(json.dumps(data, indent=4))


def error(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit()


def main(arguments):
    # define indexer arguments/parameter input
    ACTIONS = ('index', 'list', 'get', 'cluster')
    GET_ACTIONS = ('term', 'tweet', 'idf', 'tfidf')

    parser = argparse.ArgumentParser(prog="Indexer", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", metavar='action', type=str, nargs='+',
                        help='Actions for the indexer: %s' % ', '.join(ACTIONS))
    parser.add_argument("--file", metavar='file', type=str, help='Input file used for indexing actions')
    parser.add_argument("--version", action='store_true', default=False, help="current version")
    args = parser.parse_args(arguments)

    if args.version:
        error("Indexer - Version: %d.%d.%d" % VERSION)

    indexer = Indexer()

    # 
    # PARSE ARGUMENTS
    #
    if not args.action[0] in ACTIONS:
        error("Action not recognized, try: %s" % ', '.join(ACTIONS))
    ACTION = args.action[0]

    if ACTION == "index":
        indexer.IndexFile(args.file)
    else:
        indexer.LoadIndexes()

    if ACTION == 'get':

        if not len(args.action) > 2:
            error("Expected extra parameter(s)")

        if not args.action[1] in GET_ACTIONS:
            error("Invalid parameter, try: %s" % ', '.join(GET_ACTIONS))

        ACTION_GET = args.action[1]
        ACTION_GET_VAL = args.action[2]

        if ACTION_GET == 'term':
            tweets = indexer.GetTweetsForTerm(ACTION_GET_VAL)
            for tweet in tweets:
                print(tweet)

        elif ACTION_GET == 'tweet':
            print(indexer.GetTweetForTweetid(ACTION_GET_VAL))

        elif ACTION_GET == 'idf':
            print(indexer.GetIDFForTerm(ACTION_GET_VAL))

        elif ACTION_GET == 'tfidf':
            if not len(args.action) > 3:
                error("Expected extra parameter: tweetid")
            print(indexer.GetTFIDFForTerm(ACTION_GET_VAL, args.action[3]))

    elif ACTION == 'cluster':

        if not len(args.action) > 1:
            error("Expected extra parameter(s)")

        ACTION_CLUSTER_VAL = args.action[1]

        indexer.ClusterTerms(ACTION_CLUSTER_VAL)

    elif ACTION == 'list':
        indexer.List()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
