#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Roy Haanen - 12/10/2014 
#
# CHANGELOG
# 0.0.1     Setup initial NoiseFilter class
# 0.0.2     Added IDF

VERSION = (0,0,2)
 
import os
import re
import sys
import math
import argparse

sys.path.insert(0,"../indexer")
from indexer import Indexer


class NoiseFilter:

    """
    NoiseFilter takes a list of Unidentified Terms (UTs), filters out noise (garbage) and returns a (noise)filtered list of UTs

    """
    
    def __init__(self, args):
        
        self.args = args

        # define noisefilter arguments/parameter input
        self.ACTIONS = ('filter')
        
        # parse noisefilter action
        if not args.action[0] in self.ACTIONS:
            error("Action not recognized, try: %s" % ', '.join(self.ACTIONS))
        self.ACTION = args.action[0]
        
        # instance variables
        self.output_filename = "ut_filtered.txt"
        self.output_filename_regex = "ut_filtered_regex.txt"
        self.output_filename_idf = "ut_filtered_idf.txt"

        self.output_filename_noise = "ut_noise.txt"
        self.output_filename_noise_regex = "ut_noise_regex.txt"
        self.output_filename_noise_idf = "ut_noise_idf.txt"
        
        self.PerformAction()
    
    def PerformAction(self):
            
        if self.ACTION == 'filter':
            self.FilterNoise(self.args.file)
        
    def FilterNoise(self, fname):
        
        # make sure file exists
        if not os.path.isfile(fname):
            error("Provided file does not exist?")
        
        # read file and itterate over the lines
        with open(fname) as fd:

            content = fd.readlines()
            unfiltered_terms = []
            filtered_terms_regex = []
            filtered_terms_idf = []
            combined_filtered_terms = []
            noise_terms_regex = []
            noise_terms_idf = []
            combined_noise_terms = []

            # Create an instance of the indexer
            indexer = Indexer()
            # Index the tweets
            indexer.LoadIndexes()

            # Regexes to use as a filter
            ONLYNUM     = "^[0-9]*$"
            SPECIAL     = "[/_$&+,:;{}\"=?\[\]@#|~'<>^*()%!]"
            NON_ASCII   = "[^\x00-\x7F]"
            PUNCT       = "[.?\-\",]"
            CONSONANT   = "(^y|[bBcCdDfFgGhHjJkKlLmMnNpPqQrRsStTvVwWxXyYzZ])"
            VOWEL       = "([aAeEiIoOuU])"
            CONSONANT_4 = "[bBcCdDfFgGhHjJkKlLmMnNpPqQrRsStTvVwWxXyYzZ]{4}"
            VOWEL_4     = "[aAeEiIoOuU]{4}"
            
            for line in content:
                
                term = line.strip().split('\t')[0]

                unfiltered_terms.append(term)
                
                # Applied filters:
                # 1. terms of 1 or 2 characters or terms larger than 10 characters
                # 2. terms containing non-ascii characters
                # 3. terms containing special characters
                # 4. terms consisting only of numbers
                # 5. terms having more punctuation than characters
                # 6. Four or more consecutive vowels, or five or more consecutive consonants.
                
                if (len(term) <3 or len(term) >= 7) \
                or (re.search(NON_ASCII,term) != None) \
                or (re.search(SPECIAL,term) != None) \
                or (re.search(ONLYNUM,term) != None) \
                or (len(re.findall(PUNCT,term)) > (len(term)-len(re.findall(PUNCT,term)))) \
                or (re.search(VOWEL_4,term) != None) or (re.search(CONSONANT_4,term) != None) \
                :
                    noise_terms_regex.append(term)
                
                else: 
                    filtered_terms_regex.append(term)
            
                # Get IDF term values. idf_base is the idf factor for terms that only appear once in the whole collection.
                # Values lower than the idf_base can be a valid UTs, otherwise not
                idf = indexer.GetIDFForTerm(term)
                doccount = float(len(indexer.index_tweets.keys()))
                idf_base = math.log(doccount)
                threshold_idf = self.args.idf_factor*idf_base
                
                if idf <= threshold_idf:
                    filtered_terms_idf.append(term)
                else:
                    noise_terms_idf.append(term)

            combined_filtered_terms = intersect(filtered_terms_regex,filtered_terms_idf)
            combined_noise_terms = diff(unfiltered_terms,combined_filtered_terms)

            print 'Input Terms: ' + str(len(unfiltered_terms))
            print 'Unidentified Terms Regex: ' + str(len(filtered_terms_regex))
            print 'Noisy Terms Regex: ' + str(len(noise_terms_regex))
            print 'Unidentified Terms IDF: ' + str(len(filtered_terms_idf))
            print 'Noisy Terms IDF: ' + str(len(noise_terms_idf))
            print 'Combined Unidentified Terms: ' + str(len(combined_filtered_terms))
            print 'Combined Noisy Terms: ' + str(len(combined_noise_terms))
        
            with open(self.output_filename_regex, 'w') as outputfile_regex:
                for ut in filtered_terms_regex:
                    outputfile_regex.write(ut + '\n')

            with open(self.output_filename_noise_regex, 'w') as outputfile_noise_regex:
                for nt in noise_terms_regex:
                    outputfile_noise_regex.write(nt + '\n')

            with open(self.output_filename_idf, 'w') as outputfile_idf:
                for ut in filtered_terms_idf:
                    outputfile_idf.write(ut + '\n')

            with open(self.output_filename_noise_idf, 'w') as outputfile_noise_idf:
                for nt in noise_terms_idf:
                    outputfile_noise_idf.write(nt + '\n')

            with open(self.output_filename, 'w') as outputfile:
                for ut in combined_filtered_terms:
                    outputfile.write(ut + '\n')

            with open(self.output_filename_noise, 'w') as outputfile_noise:
                for nt in combined_noise_terms:
                    outputfile_noise.write(nt + '\n')

def intersect(a, b):
    return list(set(a) & set(b))

def diff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]

def error(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit()

def main(arguments):
    
    parser = argparse.ArgumentParser(prog="NoiseFilter", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", metavar='action', type=str, nargs='+', help='Action for NoiseFilter: filter')
    parser.add_argument("--file", metavar='file', type=str, help='Input file used for filtering actions')
    parser.add_argument("--idf_factor", metavar='idf_factor', type=float, help='Multiply base idf with factor 0.0..1.0')
    parser.add_argument("--version", action='store_true', default=False, help="current version")
    args = parser.parse_args(arguments)
    
    if args.version:
        error("NoiseFilter - Version: %d.%d.%d" % VERSION)
    
    noisefilter = NoiseFilter(args)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
