import run_APGC
from flair.data import Sentence
import spacy
from flair.models import MultiTagger
import networkx as nx
import matplotlib.pyplot as plt
from flair.tokenization import SciSpacyTokenizer
import pprint
class BU_SchemaGenerator():
    def __init__(self):
        self.tagger = MultiTagger.load("hunflair")
        self.tag_dictionary = {}
        self.nlp = spacy.load("en_core_web_lg")
    def run_flairTagger(self,g):
        for node in list(g.nodes):
            doc = self.nlp(str(node))
            Cnode = str(node)
            for token in doc:
                if str(token.tag_) == "ROOT":
                    node  = token.text
            s = Sentence(str(node))
            self.tagger.predict(s)
            for entity in s.get_spans(min_score = 0.7):
                self.tag_dictionary[str(Cnode)] = str(entity.get_labels()[0]).split(' ')[0]
                break
                

gc = run_APGC.GraphConstructor('sample.txt')
gc.run_pipeline()
sg = BU_SchemaGenerator()
sg.run_flairTagger(gc.DbankGraph)
G = nx.relabel_nodes(gc.DbankGraph, sg.tag_dictionary)
print(sg.tag_dictionary)
pos = nx.spring_layout(G)
plt.figure(figsize=(40, 40))
nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
        node_size=500, node_color='skyblue', alpha=0.9,
        labels={node: node for node in G.nodes()})
plt.axis('off')
plt.show()