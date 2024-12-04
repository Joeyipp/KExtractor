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

class dbpedia_linker():
    def __init__(self,entity,nlp,g) :
        self.entity = entity
        self.nlp = nlp
        self.g = g
    def linker(self):
        d = self.entity
        uri = []
        if is_ascii(d):
            if len(d.split(' ')) == 1:
                try : 
                    self.g.parse('http://dbpedia.org/resource/' + str(d))
                except Exception as e:
                    print("failed")
                if len(self.g)>0:
                    uri = ['http://dbpedia.org/resource/' + str(d)]
                else :
                    try :
                        doc = self.nlp(d)
                        uri = [(ent.text, ent.label_, ent.kb_id_) for ent in doc.ents]
                    except ValueError :
                        print("failed")
            elif len(d.split(' ')) > 1:
                try :
                    doc = self.nlp(d)
                    uri = [(ent.text, ent.label_, ent.kb_id_) for ent in doc.ents]
                    if len(uri) > 1:
                        d = d.replace(' ','_').capitalize()
                        self.g.parse('http://dbpedia.org/resource/' + str(d))
                        if len(self.g)>0:
                            uri = ['http://dbpedia.org/resource/' + str(d)]
                except Exception:
                    print("failed")
        if len(uri) == 1:
            if type(uri[0]) == str:
                self.uri = uri[0]
            elif type(uri[0]) == tuple:
                self.uri = uri[0][-1]

# g = Graph()
# nlp = spacy.load('en_core_web_lg')
# nlp.add_pipe('dbpedia_spotlight')
# d = dbpedia_linker("Asperger Syndrome",nlp,g)
# d.linker()
# print(d.uri)