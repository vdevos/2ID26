#!/usr/bin/env python

# Roy Haanen - 12/10/2014 
#
# CHANGELOG
# 0.0.1     Setup initial filter_noise class

VERSION = (0,0,2)
 
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
            UPPER       = "[A-Z]"
            LOWER       = "[a-z]"
            PUNCT       = "[.?\-\",]"
            ALL_ALPHA   = "^[a-z]+$"
            CONSONANT   = "(^y|[bBcCdDfFgGhHjJkKlLmMnNpPqQrRsStTvVwWxXyYzZ])"
            VOWEL       = "([aAeEiIoOuU])"
            CONSONANT_5 = "[bBcCdDfFgGhHjJkKlLmMnNpPqQrRsStTvVwWxXyYzZ]{5}"
            VOWEL_5     = "[aAeEiIoOuU]{5}"
            REPEATED    = "(\b\S{1,2}\s+)(\S{1,3}\s+){5,}(\S{1,2}\s+)"
            
            for line in content:
                
                term = line.strip().split('\t')[0]

                unfiltered_terms.append(term)
                
                # Applied filters:
                # 1. terms of 1 or 2 characters or terms larger than 10 characters
                # 2. terms containing special characters
                # 3. terms consisting only of numbers
                # 4. terms having more punctuation than characters
                # 5. Four or more consecutive vowels, or five or more consecutive consonants.
                if (len(term) <3 or len(term) >= 5) \
                or (re.search(SPECIAL,term) != None) \
                or (re.search(ONLYNUM,term) != None) \
                or (len(re.findall(PUNCT,term)) > (len(term)-len(re.findall(PUNCT,term)))) \
                or (re.search(VOWEL_5,term) != None) or (re.search(CONSONANT_5,term) != None) \
                :
                    noise_terms_regex.append(term)
                
                else: 
                    filtered_terms_regex.append(term)
            
                # Get IDF term values. If > 0.0 it can be a valid UT, otherwise not
                idf = indexer.GetIDFForTerm(term)
                if idf > 0.0:
                    filtered_terms_idf.append(term)
                elif idf == 0.0:
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
    parser.add_argument("--version", action='store_true', default=False, help="current version")
    args = parser.parse_args(arguments)
    
    if args.version:
        error("NoiseFilter - Version: %d.%d.%d" % VERSION)
    
    noisefilter = NoiseFilter(args)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
