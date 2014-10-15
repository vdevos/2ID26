__author__ = 'Thom Hurks'

# Assumption: using Python 3.4, not tested with other versions.
# Directions: you have installed NLTK and used NLTK.download() to download all NLTK data.
# In the same directory as this file, you should have an input file and a world list file with the specified names.
# OPTIONAL: For the NER tagger you need a classifier and the Stanford NER jar file. Together they are 28 MB.

import nltk
from nltk.corpus import words
from nltk.stem import snowball
from nltk.tag.stanford import *

# Write UT's to file:
write_output = True
output_filename = "ut_output.txt"
# NER tagging is very slow! For now just prints to console.
apply_NER_tagging = False
# Input file:
tweetsfilename = "tweets.txt"
# English word list file name:
dictFileName = "wordsEn.txt"

# The Snowball stemmer is basically "Porter v2".
# There is also the Lancaster stemmer, but it is quite aggressive.
# Another approach could be lemmatization using Wordnet.
stemmer = snowball.EnglishStemmer()
tweets = []
tokens = set()
normalized_tweets = []

# First we read in all the tweets.
if os.path.isfile(tweetsfilename):
    with open(tweetsfilename) as tweetsfile:
        lines = tweetsfile.readlines()
        for line in lines:
            linedata = line.strip().split('\t')
            if len(linedata) >= 6:
                tweets.append(linedata[5])

if apply_NER_tagging:
    # Apply the Stanford Named Entity Recognizer (NER) tagger.
    nertagger = NERTagger('english.all.3class.distsim.crf.ser.gz', 'stanford-ner-3.4.1.jar', 'utf-8')
    # Tokenize the tweets with the NLTK default tokenizer and apply the NER tagger on the tweets.
    # Todo: store and cache the tagging output with pickle or something.
    for tweet in tweets:
        tweet_tokens = nltk.word_tokenize(tweet)
        tagged_tweet = nertagger.tag(tweet_tokens)
        print(tagged_tweet)

# Tokenize the tweets with the NLTK default tokenizer.
for tweet in tweets:
    tweet_tokens = nltk.word_tokenize(tweet)
    for token in tweet_tokens:
        tokens.add(token)

# Make a copy of the tokens, we will use this set to remove identified tokens from
unidentified_terms = set(tokens)

# Get the NLTK "words" corpus as a set
wordlist = set(words.words())

# Read in the English dictionary and merge it with the NLTK words corpus
if os.path.isfile(dictFileName):
    with open(dictFileName) as dictFile:
        lines = dictFile.readlines()
        for word in lines:
            wordlist.add(word)

# Remove all tokens that appear in the dictionary directly (lowercase)
for token in tokens:
    if token.lower() in wordlist:
        unidentified_terms.remove(token)

# To filter more words, we need to apply stemming.
stemmed_wordlist = dict()

for word in wordlist:
    stemmedWord = stemmer.stem(word)
    stemmed_wordlist[stemmedWord] = word

print("nr of unidentified terms before stemming: ", len(unidentified_terms))

copy_of_uts = set(unidentified_terms)
for token in copy_of_uts:
    stemmedToken = stemmer.stem(token.lower())
    result = stemmed_wordlist.get(stemmedToken, None)
    if result is not None:
        unidentified_terms.remove(token)
del copy_of_uts

print("nr of words in wordlist: ", len(wordlist))
print("nr of extracted tokens: ", len(tokens))
print("nr of unidentified terms: ", len(unidentified_terms))

if write_output:
    # The 'w' means open for exclusive creation, failing if the file already exists.
    with open(output_filename, 'x') as outputfile:
        for ut in unidentified_terms:
            outputfile.write(ut + '\n')

exit()