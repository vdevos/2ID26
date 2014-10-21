#!/bin/sh

verb()
{
    read -p ""
}


echo "IR Task 1 - Tokenize & Normalize Tweets"
echo ""
cat ut_recognizer/normalized_filtered_tweets.txt | head -n 15
verb

echo "IR Task 1 - Extract Unidentified Terms (still with noisy terms)"
echo ""
cat ut_recognizer/ut_output.txt | head -n  25
verb

echo "IR Task 3 - Filter Noisy Terms"
echo ""
cat ut_noisefilter/ut_filtered.txt | head -n 25
verb

echo "IR Task 2 - Build inverted Index"
indexer/indexer.py list
verb

echo "IR Task 4 - Build Ranking"
echo ""
cat ut_tweetrank/ut_ranked.txt | head -n  10
verb

echo "DM Task 5 - Determine Context - Example terms: wild, app, edm, bro, 21st"
echo ""
echo "wild: `indexer/indexer.py apriori 'wild'`"
echo "app: `indexer/indexer.py apriori 'app'`"
echo "EDM: `indexer/indexer.py apriori 'edm'`"
echo "Bro: `indexer/indexer.py apriori 'bro'`"
echo "21st: `indexer/indexer.py apriori '21st'`"
verb

echo "DM Task 6 - Cluster Terms"
echo ""
echo "Clustered Terms: "
echo ""
cat ut_recognizer/term_cooccurrence_output.txt | head -n 15
echo ""
echo "Named Entity Recognition (NER)"
echo ""
cat ut_recognizer/tagger_output.txt | head -n 10
verb

read -p "Get results for input:" term
echo ""
echo "Get: Clustered Terms"
echo ""
cat ut_recognizer/term_cooccurrence_output.txt | grep -i "${term}"
echo ""
echo "Get: Context for term"
echo ""
indexer/indexer.py apriori "${term}"
echo ""
echo "Get: Ranking"
echo ""
cat ut_tweetrank/ut_ranked.txt | grep -i "${term}"
exit
echo "Input: Raw Tweets"
echo ""
cat ut_recognizer/tweets.txt | head -n 15
verb 
exit

