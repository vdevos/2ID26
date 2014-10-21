__author__ = 'Thom Hurks'

import os
import operator
import sys

from nltk.corpus import stopwords

sys.path.insert(0, "../ut_tweetrank")
from tweetrank import TweetRank
sys.path.insert(0, "../indexer")
from indexer import Indexer

output_filename = "term_cooccurrence_output"
output_extension = ".txt"
# Input files:
input_tweets_filename = "normalized_filtered_tweets.txt"
tweet_text_column_index = 5
input_unidentified_terms_filename = "ut_output.txt"

stopwords_set = set(stopwords.words('english'))
tweets = []
unidentified_terms = set()
# The minimum number of times a words should co-occur with a UT before we record it.
minimal_nr_occurrences = 60
# The maximum nr of co-occurring words that we record per UT.
max_words = 5

tweet_indexer = Indexer()
tweet_indexer.LoadIndexes()

# First we read in all the tweets.
if os.path.isfile(input_tweets_filename):
    with open(input_tweets_filename) as tweetsfile:
        lines = tweetsfile.readlines()
        for line in lines:
            linedata = line.strip().split('\t')
            if len(linedata) >= tweet_text_column_index + 1:
                tweet_text = set(linedata[tweet_text_column_index].strip().split(' '))
                tweet_text = tweet_text - stopwords_set
                tweets.append(tweet_text)
            else:
                print(str(linedata))
                print("Invalid file format!")

print("Nr of tweets read in: ", len(tweets))

# Read in the unidentified terms
if os.path.isfile(input_unidentified_terms_filename):
    with open(input_unidentified_terms_filename) as utsFile:
        lines = utsFile.readlines()
        for ut in lines:
            unidentified_terms.add(ut.strip())

print("Nr of unidentified terms read in: ", len(unidentified_terms))
#print(str(unidentified_terms))
ut_cooccurrences = dict()

# Here, we count the words that co-occur with an unidentified term.
for tweet in tweets:
    tweet = set(tweet)
    common_uts = tweet.intersection(unidentified_terms)
    for ut in common_uts:
        count_dict = ut_cooccurrences.get(ut, None)
        if count_dict is None:
            count_dict = dict()
        for word in tweet:
            if word is not ut:
                count = count_dict.get(word, None)
                if count is None:
                    count = 1
                else:
                    count += 1
                count_dict[word] = count
        ut_cooccurrences[ut] = count_dict

tweet_ranker = TweetRank(None)
ranked_tweets = tweet_ranker.TweetRank({"yolo"})
for (tweetid, score) in ranked_tweets:
    print(tweet_indexer.GetTweetForTweetid(tweetid))

# Write the term with corresponding ranked tweet ids & scores to file
if False:
    with open(self.output_filename, 'w') as outputfile:
        for ut in unidentified_terms:
            outputfile.write(ut + '\t')
            number_rankings = len(self.sorted_cropped_rankings[ut])

            for i in range(0, number_rankings):
                outputfile.write(str(self.sorted_cropped_rankings[ut][i]) + '\t')

            outputfile.write('\n')

written = False
file_counter = 0
tab = str('\t')
newline = str('\n')
comma = str(',')
while not written:
    try:
        # The 'w' means open for exclusive creation, failing if the file already exists.
        with open(output_filename + str(file_counter) + output_extension, 'x') as outputfile:
            for ut in ut_cooccurrences.keys():
                count_dict_items = ut_cooccurrences[ut].items()
                # Apply some basic filtering by requiring min nr of co-occurences and capping the nr of words.
                count_dict_items = sorted(count_dict_items, key=operator.itemgetter(1), reverse=True)
                word_counter = 0
                line = ut
                for (word, occurrences) in count_dict_items:
                    if occurrences >= minimal_nr_occurrences and word_counter < max_words:
                        line += tab + word + comma + str(occurrences)
                        word_counter += 1
                if word_counter >= 1:
                    outputfile.write(line + newline)
            written = True
    except FileExistsError:
        file_counter += 1

print("Done.")
