__author__ = 'thom'

import sys
sys.path.insert(0,"../ut_noisefilter")
import nltk
import os
from nltk.stem import snowball
from noisefilter import NoiseFilter

# Input file:
input_tweets_filename = "tweets.txt"
output_filename = "normalized_tweets"
output_extension = ".txt"
tweet_text_column_index = 5

# The Snowball stemmer is basically "Porter v2".
# There is also the Lancaster stemmer, but it is quite aggressive.
stemmer = snowball.EnglishStemmer()
tweets = []
normalized_tweets = []

old_tweets = []

# First we read in all the tweets.
if os.path.isfile(input_tweets_filename):
    with open(input_tweets_filename) as tweetsfile:
        lines = tweetsfile.readlines()
        for line in lines:
            linedata = line.strip().split('\t')
            if len(linedata) >= tweet_text_column_index + 1:
                old_tweets.append(linedata)
                tweets.append(linedata[tweet_text_column_index])
            else:
                print("Invalid file format!")
                exit()

assert len(old_tweets) == len(tweets)

# Tokenize the tweets with the NLTK default tokenizer.
for tweet in tweets:
    tweet_tokens = nltk.word_tokenize(tweet)
    normalized_tweet = []
    for token in tweet_tokens:
        if len(token) > 1:
            stemmed_token = stemmer.stem(token.lower())
            if len(stemmed_token) > 1:
                normalized_tweet.append(stemmed_token)
    normalized_tweets.append(normalized_tweet)

assert len(old_tweets) == len(normalized_tweets)

# This should output "test".
noise_filter = NoiseFilter(None)
filtered_words = noise_filter.FilterNoise({"test", "blablablablabla"}, 0.8)
print(str(filtered_words))

space = str(' ')
tab = str('\t')
written = False
file_counter = 0
while not written:
    try:
        # The 'w' means open for exclusive creation, failing if the file already exists.
        with open(output_filename + str(file_counter) + output_extension, 'x') as outputfile:
            line_index = 0
            for tweet in normalized_tweets:
                line = str()
                old_tweet = old_tweets[line_index]
                column_index = 0
                for column in old_tweet:
                    if column_index < tweet_text_column_index:
                        line += column + tab
                    column_index += 1
                for token in tweet:
                    line += token + space
                column_index = 0
                for column in old_tweet:
                    if column_index > tweet_text_column_index:
                        line += tab + column
                    column_index += 1
                outputfile.write(line + '\n')
                line_index += 1
            written = True
    except FileExistsError:
        file_counter += 1