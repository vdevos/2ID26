__author__ = 'thom'

import nltk
import os
from nltk.stem import snowball


# Input file:
tweetsfilename = "tweets.txt"
output_normalizedtweets_filename = "normalized_tweets.txt"

# The Snowball stemmer is basically "Porter v2".
# There is also the Lancaster stemmer, but it is quite aggressive.
stemmer = snowball.EnglishStemmer()
tweets = []
normalized_tweets = []


# First we read in all the tweets.
if os.path.isfile(tweetsfilename):
    with open(tweetsfilename) as tweetsfile:
        lines = tweetsfile.readlines()
        for line in lines:
            linedata = line.strip().split('\t')
            if len(linedata) >= 6:
                tweets.append(linedata[5])

# Tokenize the tweets with the NLTK default tokenizer.
for tweet in tweets:
    tweet_tokens = nltk.word_tokenize(tweet)
    normalized_tweet = []
    for token in tweet_tokens:
        if len(token) > 1:
            stemmed_token = stemmer.stem(token.lower())
            if len(stemmed_token) > 1:
                normalized_tweet.append(stemmed_token)
    if len(normalized_tweet) > 0:
        normalized_tweets.append(normalized_tweet)

space = str(' ')
# The 'w' means open for exclusive creation, failing if the file already exists.
with open(output_normalizedtweets_filename, 'x') as outputfile:
    for tweet in normalized_tweets:
        line = str()
        for token in tweet:
            line += token + space
        outputfile.write(line + '\n')