import json
from urllib.error import HTTPError
import spacy_dbpedia_spotlight
import spacy
from random import sample
from rdflib import Graph
from rdflib.plugin import register, Serializer
from spacy.util import filter_spans
import pickle
import re


def is_ascii(s):
    return all(ord(c) < 128 for c in s)

class dbpedia_extractor():
    def __init__(self,uri,g,preds):
        self.preds = preds
        self.uri = uri
        self.g = g
        self.g.parse(self.uri)
    def triples_extractor(self):
        self.triples = []
        self.wikiURI = ''
        self.drugbankID = ''
        for s,p,o in self.g:
            if 'wikiPageRedirects' in str(p) and self.uri == str(s) and 'http' in str(s) and 'http' in str(o):
                self.triples = []
                self.uri = str(o)
                redirectGraph = Graph()
                redirectGraph.parse(self.uri) 
                for s,p,o in redirectGraph:
                    
                    if s != o and is_ascii(s) and is_ascii(o) and str(p) in self.preds:
                        if 'owl#sameAs' in str(p) and 'wikidata' in o:
                            self.wikiURI = str(o)
                        self.triples.append((str(s),str(p),str(o),"DBpedia"))
                        if 'drugbank' in str(p) :
                            self.drugbankID = str(o)

                    
                break

            if s != o and is_ascii(s) and is_ascii(o) and str(p) in self.preds:
                if 'owl#sameAs' in str(p) and 'wikidata' in o:
                    self.wikiURI = str(o)
                self.triples.append((str(s),str(p),str(o),"DBpedia"))
                if 'drugbank' in str(p) :
                    self.drugbankID = str(o)


# g = Graph()
# nlp = spacy.load('en_core_web_lg')
# nlp.add_pipe('dbpedia_spotlight')
# d = dbpedia_extractor("http://dbpedia.org/resource/Aspirin",g)
# d.triples_extractor()
# print(d.drugbankID)
