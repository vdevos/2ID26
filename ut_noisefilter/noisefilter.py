#!/usr/bin/env python

# Roy Haanen - 12/10/2014 
#
# CHANGELOG
# 0.0.1     Setup initial filter_noise class

VERSION = (0,0,1)
 
import os
import re
import sys
import json
import math
import pickle
import operator
import argparse
#import indexer

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
        self.ut_filtered = {}
        self.output_filename = "ut_filtered.txt"
        self.output_filename_noise = "ut_noise.txt"
        
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
            # filtered_terms is the array to be filled with filtered terms, noise_terms the garbage
            filtered_terms = []
            noise_terms = []

            # Cached regexes we plan on using.
            ONLYNUM     = "^[0-9]*$"
            SPECIAL     = "[/_$&+,:;{}\"=?\[\]@#|~'<>^*()%!]"
            UPPER       = "[A-Z]"
            LOWER       = "[a-z]"
            PUNCT       = "[.?\-\",]"
            ALL_ALPHA   = "^[a-z]+$"
            CONSONANT   = "(^y|[bcdfghjklmnpqrstvwxyz])"
            VOWEL       = "([aAeEiIoOuU])"
            CONSONANT_5 = "[bBcCdDfFgGhHjJkKlLmMnNpPqQrRsStTvVwWxXyYzZ]{5}"
            VOWEL_5     = "[aAeEiIoOuU]{5}"
            REPEATED    = "(\b\S{1,2}\s+)(\S{1,3}\s+){5,}(\S{1,2}\s+)"
            SINGLETONS  = "^[AaIi]$"
        
            for line in content:
                
                term = line.strip().split('\t')[0]

                unfiltered_terms.append(term)
                
                # Applied filters:
                # 1. terms of 1 or 2 characters or terms larger than 10 characters
                # 2. terms containing special characters
                # 3. terms consisting only of numbers
                # 4. terms having more punctuation than characters
                # 5. Four or more consecutive vowels, or five or more consecutive consonants.
                if (len(term) <3 or len(term) >= 10) \
                or (re.search(SPECIAL,term) != None) \
                or (re.search(ONLYNUM,term) != None) \
                or (len(re.findall(PUNCT,term)) > (len(term)-len(re.findall(PUNCT,term)))) \
                or (re.search(VOWEL_5,term) != None) or (re.search(CONSONANT_5,term) != None) \
                :
                    noise_terms.append(term)
                
                else: 
                    filtered_terms.append(term)
            
            print 'Input Terms: ' + str(len(unfiltered_terms))
            print 'Unidentified Terms: ' + str(len(filtered_terms))
            print 'Noisy Terms: ' + str(len(noise_terms))
        
            with open(self.output_filename, 'w') as outputfile:
                for ut in filtered_terms:
                    outputfile.write(ut + '\n')

            with open(self.output_filename_noise, 'w') as outputfile_noise:
                for nt in noise_terms:
                    outputfile_noise.write(nt + '\n')
    
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
