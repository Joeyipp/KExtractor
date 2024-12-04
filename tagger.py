from flair.data import Sentence
import matplotlib.pyplot as plt
import spacy
import concurrent.futures
from flair.models import MultiTagger
import json
from random import sample
import time
import networkx as nx
import pprint
from flair.tokenization import SciSpacyTokenizer
nodes = []
tag_dict = {}
tagger = MultiTagger.load("hunflair")
with open("triples.txt","r") as file:
    lines = file.readlines()
triples = {}
for l in lines:
    l = l[1:-2].strip("'")
    l = l.split(',')
    s = l[0].replace("'","").split('/')[-1]
    p = l[1].replace("'","")
    o = l[2].replace("'","").split('/')[-1]
    nodes.append(s.lower())
    nodes.append(o.lower())
nodes = list(set(nodes))
nodes = sample(nodes,50)
print(len(nodes))
num_ents = len(nodes)
def etagger(start,end,tagger):
    type_dict = []
    print("Entry")
    for node in nodes[start:end]:
        node = node.split('/')[-1]
        node = node.replace('_',' ')
        print(node)
        s = Sentence(str(node))
        tagger.predict(s)
        for entity in s.get_spans(min_score = 0.7):
            type_dict.append((node,str(entity.get_labels()[0]).split(' ')[0]))
    return type_dict

type_dict = etagger(0,num_ents,tagger)

for t in type_dict:
    tag_dict[t[0]] = t[1]
with open('tag_dict.json', 'w') as fp:
    json.dump(tag_dict, fp)
