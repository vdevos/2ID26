#2ID26

### Members
Vincent de Vos, Roy Haanen, Thom Hurks

### Demo instructions 
Run `pipeline.sh` in the root directory

### Packages

NLTK
1. http://www.nltk.org/install.html
2. Download NLTP packages

### Motivation
Content from users on Twitter is restricted to 140 characters. This introduces the use of abbreviations by these users. Also the usage of slang is quite common and because most users are human you will also see spelling mistakes. All these cases introduce so-called un- identified terms. By this we mean a word that cannot be recognized as a known word because it does not occur in a known English lexicon.

### Goal
It would be useful to create some context around such an un-identified term (UT) and maybe even take a guess at what it actually refers to. To be able to say anything about a UT extra information is required. This information (like frequently co-occurring terms of the UT) should be gathered from other tweets, which are most relevant to the UT. If enough qualitative info is gathered, by aggregating all information a meaning or context of the unidentified term can be given.

### Data input
For this task only English Tweets from Twitter are used.

