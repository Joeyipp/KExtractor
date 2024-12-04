from pydoc import cli
from wikidata.client import Client
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
class wikidata_extractor():
    def __init__(self,code,g,preds):
        self.code = code
        self.preds = preds
        print(self.code)
        self.g = g
        self.g.parse('https://www.wikidata.org/wiki/Special:EntityData/' + self.code + '.nt')
    def triples_extractor(self):
        self.triples = []
        for s,p,o in self.g:
            if s != o and is_ascii(s) and is_ascii(o) :
                self.triples.append((str(s),str(p),str(o),"wikidata"))
                # if p.split('/')[-1] in self.preds or 'name' in p.split('/')[-1]:
                #     self.triples.append((str(s),str(p),str(o),"wikidata"))
                    # doctest: +SKIP
                    # try:
                    #     client = Client()
                    #     entity = client.get(str(p.split('/')[-1]), load=True)
                    #     e = entity.__dict__['data']['labels']['en']['value']
                    #     if 'wikipedia' not in str(s) and 'wikipedia' not in str(o):
                    #         self.triples.append((str(s),str(e),str(o),"wikidata"))
                    #     print((str(s),str(e),str(o)))
                    # except Exception:
                    #     print(s,p,o)
                    #     pass
               

                    

# g = Graph()
# d = wikidata_extractor('',g)
# d.triples_extractor()
# print(d.triples)