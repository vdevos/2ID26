__author__ = 'thom'

import nltk
from nltk.stem import snowball
from nltk.tag.stanford import *

stemmer = snowball.EnglishStemmer()
# Apply the Stanford Named Entity Recognizer (NER) tagger.
nertagger = NERTagger('english.all.3class.distsim.crf.ser.gz', 'stanford-ner-3.4.1.jar', 'utf-8')

output_filename = "tagger_output"
output_extension = ".txt"
# NER tagging is very slow! For now just prints to console.
# Input file:
tweetsfilename = "tweets.txt"

tweets = []
tagged_tokens = dict()

# First we read in all the tweets.
if os.path.isfile(tweetsfilename):
    with open(tweetsfilename) as tweetsfile:
        lines = tweetsfile.readlines()
        for line in lines:
            linedata = line.strip().split('\t')
            if len(linedata) >= 6:
                tweets.append(linedata[5])

# Tokenize the tweets with the NLTK default tokenizer and apply the NER tagger on the tweets.
# Todo: store and cache the tagging output with pickle or something.
counter = 0
for tweet in tweets:
    tweet_tokens = nltk.word_tokenize(tweet)
    try:
        tagged_tweet = nertagger.tag(tweet_tokens)
    except UnicodeDecodeError:
        print(tweet_tokens)
        pass
    for (token, tag) in tagged_tweet:
        stemmed_token = stemmer.stem(token.lower())
        if len(stemmed_token) > 1 and tag != 'O':
            print(tag)
            tags_set = tagged_tokens.get(stemmed_token, None)
            if tags_set is None:
                tags_set = set()
                tags_set.add(tag)
                tagged_tokens[stemmed_token] = tags_set
            else:
                tags_set = set(tags_set)
                tags_set.add(tag)
                tagged_tokens[stemmed_token] = tags_set
    counter += 1
    print(counter)

comma = str(',')
tab = str('\t')
written = False
counter = 0
while not written:
    try:
        # The 'w' means open for exclusive creation, failing if the file already exists.
        with open(output_filename + str(counter) + output_extension, 'x') as outputfile:
            for token in tagged_tokens.keys():
                line = token + tab
                for tag in tagged_tokens.get(token):
                    line += tag + comma
                outputfile.write(line + '\n')
            written = True
    except FileExistsError:
        counter += 1