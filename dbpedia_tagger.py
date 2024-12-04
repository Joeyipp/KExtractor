from pydbpedia import PyDBpedia, namespace
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


class dbpedia_tagger():
    def __init__(self,uri):
        self.tags = []
        try:
            uri = uri
            dbpedia_uris = [uri]
            labels = []
            dbpedia_wrapper = PyDBpedia(endpoint="http://dbpedia.org/sparql")
            objects = dbpedia_wrapper.get_objects(subjects=dbpedia_uris, predicates=[namespace.RDF_TYPE])
            for obj in objects:
                if 'http://dbpedia.org/ontology/' in obj :
                    labels.append(obj.rsplit('/', 1)[-1])
            self.tags = labels
        except Exception:
            pass

# print(dbpedia_tagger('http://dbpedia.org/resource/Aspirin').tags)
