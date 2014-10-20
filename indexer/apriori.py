#!/usr/bin/env python

# Vincent de Vos - 6/10/2014 

import sys

def TermCount(termtrans):
    adict = {}
    for t in termtrans:
        for item in t:
            if item in adict:
                adict[item] += 1
            else:
                adict[item] = 1
    return adict 

def FilterTerms(terms, min_support, tcount):
    adict={}
    for key in terms:
        ratio = float(float(terms[key])/float(tcount))
        if ratio >= min_support:
            adict[key] = terms[key]   
    return adict 

def GenerateTerms(terms):
    adict={}
    for i in terms:
        for j in terms:
            if i != j and (j,i) not in adict:
                adict[tuple([min(i,j),max(i,j)])] = 0
    return adict 

def MutateTerms(terms, termtrans):
    for key in terms:
        for t in termtrans:
            if key[0] in t and key[1] in t:
                terms[key] += 1
    return terms 

