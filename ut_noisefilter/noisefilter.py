#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Roy Haanen - 12/10/2014 
#
# CHANGELOG
# 0.0.1     Setup initial NoiseFilter class
# 0.0.2     Added IDF
# 0.0.3     Can now be called as an independent function from other files.

VERSION = (0, 0, 3)

import os
import re
import sys
import math
import argparse

sys.path.insert(0, "../indexer")
from indexer import Indexer


class NoiseFilter:
    """
    NoiseFilter takes a list of Unidentified Terms (UTs), filters out noise (garbage) and returns a (noise)filtered list of UTs

    """
    # Regexes to use as a filter
    ONLYNUM = "^[0-9]*$"
    SPECIAL = "[/_$&+,:;{}\"=?\[\]@#|~'<>^*()%!]"
    NON_ASCII = "[^\x00-\x7F]"
    PUNCT = "[.?\-\",]"
    CONSONANT_4 = "[bBcCdDfFgGhHjJkKlLmMnNpPqQrRsStTvVwWxXyYzZ]{4}"
    VOWEL_4 = "[aAeEiIoOuU]{4}"

    def __init__(self, args):

        self.args = args

        # define noisefilter arguments/parameter input
        self.ACTIONS = ('filter')

        # instance variables
        self.output_filename = "ut_filtered.txt"
        self.output_filename_regex = "ut_filtered_regex.txt"
        self.output_filename_idf = "ut_filtered_idf.txt"

        self.output_filename_noise = "ut_noise.txt"
        self.output_filename_noise_regex = "ut_noise_regex.txt"
        self.output_filename_noise_idf = "ut_noise_idf.txt"

        # global vars to store output of FilterNoise
        self.unfiltered_terms = []
        self.filtered_terms_regex = []
        self.filtered_terms_idf = []
        self.noise_terms_regex = []
        self.noise_terms_idf = []
        self.combined_filtered_terms = []
        self.combined_noise_terms = []

        # parse noisefilter action
        if args is not None:
            if not args.action[0] in self.ACTIONS:
                error("Action not recognized, try: %s" % ', '.join(self.ACTIONS))
            self.ACTION = args.action[0]
        else:
            print("No args supplied to NoiseFilter.")

        # Create an instance of the indexer
        self.indexer = Indexer()
        # Index the tweets
        self.indexer.LoadIndexes()

    def PerformAction(self):
        if self.ACTION == 'filter':
            self.FilterNoiseFromFile(self.args.file)

    def FilterNoiseFromFile(self, fname):
        # make sure file exists
        if not os.path.isfile(fname):
            error("Provided file does not exist?")

        unfiltered_terms = set()

        # read file and iterate over the lines
        with open(fname) as fd:
            lines = fd.readlines()
            for line in lines:
                term = line.strip().split('\t')[0]
                unfiltered_terms.add(term)
                self.FilterNoise(unfiltered_terms, self.args.idf_factor)
                with open(self.output_filename_regex, 'w') as outputfile_regex:
                    for ut in self.filtered_terms_regex:
                        outputfile_regex.write(ut + '\n')

                with open(self.output_filename_noise_regex, 'w') as outputfile_noise_regex:
                    for nt in self.noise_terms_regex:
                        outputfile_noise_regex.write(nt + '\n')

                with open(self.output_filename_idf, 'w') as outputfile_idf:
                    for ut in self.filtered_terms_idf:
                        outputfile_idf.write(ut + '\n')

                with open(self.output_filename_noise_idf, 'w') as outputfile_noise_idf:
                    for nt in self.noise_terms_idf:
                        outputfile_noise_idf.write(nt + '\n')

                with open(self.output_filename, 'w') as outputfile:
                    for ut in self.combined_filtered_terms:
                        outputfile.write(ut + '\n')

                with open(self.output_filename_noise, 'w') as outputfile_noise:
                    for nt in self.combined_noise_terms:
                        outputfile_noise.write(nt + '\n')

    def FilterNoise(self, unfiltered_input, idf_factor):
        self.unfiltered_terms = []
        self.filtered_terms_regex = []
        self.filtered_terms_idf = []
        self.noise_terms_regex = []
        self.noise_terms_idf = []
        self.combined_filtered_terms = []
        self.combined_noise_terms = []

        for term in unfiltered_input:

            self.unfiltered_terms.append(term)

            # Applied filters:
            # 1. terms of 1 or 2 characters or terms larger than 10 characters
            # 2. terms containing non-ascii characters
            # 3. terms containing special characters
            # 4. terms consisting only of numbers
            # 5. terms having more punctuation than characters
            # 6. Four or more consecutive vowels, or five or more consecutive consonants.

            if len(term) < 3 or len(term) >= 7 \
                    or re.search(NoiseFilter.NON_ASCII, term) is not None \
                    or re.search(NoiseFilter.SPECIAL, term) is not None \
                    or re.search(NoiseFilter.ONLYNUM, term) is not None \
                    or len(re.findall(NoiseFilter.PUNCT, term)) > (len(term) - len(re.findall(NoiseFilter.PUNCT, term))) \
                    or re.search(NoiseFilter.VOWEL_4, term) is not None \
                    or re.search(NoiseFilter.CONSONANT_4, term) is not None:
                self.noise_terms_regex.append(term)
            else:
                self.filtered_terms_regex.append(term)

            # Get IDF term values. idf_base is the idf factor for terms that only appear once
            # in the whole collection.
            # Values lower than the idf_base can be a valid UTs, otherwise not
            idf = self.indexer.GetIDFForTerm(term)
            doccount = len(self.indexer.index_tweets)
            if doccount > 0:
                idf_base = math.log(float(doccount))
            else:
                idf_base = 100.0
                print("Tried to take the log of a <= 0 doccount! Was: ", doccount)
            threshold_idf = idf_factor * idf_base

            if idf <= threshold_idf:
                self.filtered_terms_idf.append(term)
            else:
                self.noise_terms_idf.append(term)

        self.combined_filtered_terms = intersect(self.filtered_terms_regex, self.filtered_terms_idf)
        self.combined_noise_terms = diff(self.unfiltered_terms, self.combined_filtered_terms)

        print('Input Terms: ' + str(len(self.unfiltered_terms)))
        print('Unidentified Terms Regex: ' + str(len(self.filtered_terms_regex)))
        print('Noisy Terms Regex: ' + str(len(self.noise_terms_regex)))
        print('Unidentified Terms IDF: ' + str(len(self.filtered_terms_idf)))
        print('Noisy Terms IDF: ' + str(len(self.noise_terms_idf)))
        print('Combined Unidentified Terms: ' + str(len(self.combined_filtered_terms)))
        print('Combined Noisy Terms: ' + str(len(self.combined_noise_terms)))

        # This is the list we use as a result.
        return self.combined_filtered_terms


def intersect(a, b):
    return list(set(a).intersection(set(b)))


def diff(a, b):
    a_set = set(a)
    b_set = set(b)
    return list(a_set.difference(b_set))


def error(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit()


def main(arguments):
    parser = argparse.ArgumentParser(prog="NoiseFilter", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", metavar='action', type=str, nargs='+', help='Action for NoiseFilter: filter')
    parser.add_argument("--file", metavar='file', type=str, help='Input file used for filtering actions')
    parser.add_argument("--idf_factor", metavar='idf_factor', type=float, help='Multiply base idf with factor 0.0..1.0')
    parser.add_argument("--version", action='store_true', default=False, help="current version")
    args = parser.parse_args(arguments)

    if args.version:
        error("NoiseFilter - Version: %d.%d.%d" % VERSION)

    noisefilter = NoiseFilter(args)
    noisefilter.PerformAction()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))