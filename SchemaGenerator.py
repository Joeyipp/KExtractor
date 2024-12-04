
from dbpedia_tagger import dbpedia_tagger
import run_APGC
from run_APGC import createGraph
from flair.data import Sentence
import matplotlib.pyplot as plt
import spacy
import concurrent.futures
from flair.models import MultiTagger
import json
import time
import networkx as nx
import pprint
from flair.tokenization import SciSpacyTokenizer

def show_Graph(G):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(40, 40))
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
            node_size=500, node_color='skyblue', alpha=0.9,
            labels={node: node for node in G.nodes()})
    plt.axis('off')
    plt.show()
class SchemaGenerator():
    def __init__(self,G):
        self.G = G
        self.type_dict = {}
        self.tagger = MultiTagger.load("hunflair")
        self.nlp = spacy.load("en_core_web_lg")
    def run_Tagging(self,start,end):
        type_dict = {}
        tagged_predicates = []
        for node in self.G.nodes()[start:end]:
            print(node)
            if len(node.split(' ')) < 6:
                if 'dbpedia' in node:
                    Cnode = str(node)
                    node = node.split('/')[-1]
                    doc = self.nlp(str(node))
                    
                    for token in doc:
                        if str(token.tag_) == "ROOT":
                            node  = token.text
                    s = Sentence(str(node))
                    self.tagger.predict(s)
                    for entity in s.get_spans(min_score = 0.7):
                          tagged_predicates.append((Cnode,'isOfType',str(entity.get_labels()[0]).split(' ')[0]))
                          type_dict[Cnode] = str(entity.get_labels()[0]).split(' ')[0]


                    # t = dbpedia_tagger(node)
                    # tags = t.tags
                    # if len(tags)>0:
                    #     for tag in tags:
                    #         tagged_predicates.append((node,"isOftype",tag))
                elif 'wikidata' in node:
                    pass
                else :
                    doc = self.nlp(str(node))
                    Cnode = str(node)
                    for token in doc:
                        if str(token.tag_) == "ROOT":
                            node  = token.text
                    s = Sentence(str(node))
                    self.tagger.predict(s)
                    for entity in s.get_spans(min_score = 0.7):
                          tagged_predicates.append((Cnode,'isOfType',str(entity.get_labels()[0]).split(' ')[0]))
                          type_dict[Cnode] = str(entity.get_labels()[0]).split(' ')[0]
                    
        tag_graph = createGraph(tagged_predicates)
        return tagged_predicates,tag_graph,type_dict
t1 = time.time()
gc = run_APGC.GraphConstructor('sample.txt')
gc.run_pipeline()
t2 = time.time()
print("run_APGC elapsed time :",t2-t1,"s")
sample_graph = {}

schemaTrips = gc.dbtrips + gc.wtrips + gc.dbanktrips
schemaTrips = list(set(schemaTrips))


sample_graph['dbpedia'] = gc.dbtrips
sample_graph['wikidata'] = gc.wtrips
sample_graph['drugbank'] = gc.dbanktrips
G = nx.compose(gc.DBGraph,gc.DbankGraph)
G = nx.compose(gc.WikiGraph,G)
num_ents = len(G.nodes())

t1 = time.time()
sg = SchemaGenerator(G)

with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
            f1 = executor.submit(sg.run_Tagging,0,num_ents//8)
            f2 = executor.submit(sg.run_Tagging,num_ents//8,num_ents//4)
            f3 = executor.submit(sg.run_Tagging,num_ents//4 ,3*(num_ents//8))
            f4 = executor.submit(sg.run_Tagging,3*(num_ents//8),num_ents//2)
            f5 = executor.submit(sg.run_Tagging,num_ents//2,5*(num_ents//8))
            f6 = executor.submit(sg.run_Tagging,5*(num_ents//8),3*(num_ents//4))
            f7 = executor.submit(sg.run_Tagging,3*(num_ents//4) ,7*(num_ents//8))
            f8 = executor.submit(sg.run_Tagging,7*(num_ents//8),num_ents)
            while (f1.done() and f2.done() and f3.done() and f4.done() and f5.done() and f6.done() and f7.done() and f8.done())==False:
                pass
            dict_list = [f1.result()[2],f2.result()[2],f3.result()[2] ,f4.result()[2],f5.result()[2],f6.result()[2],f7.result()[2] ,f8.result()[2]]
            for d in dict_list:
                sg.type_dict.update(d)
def SchemaCreator(start,end):
    SchemaGraph = []
    for trip in schemaTrips[start:end] :
        if trip[0] in  sg.type_dict.keys() and trip[2] in  sg.type_dict.keys() and trip[1] != "http://schema.org/description":
            SchemaGraph.append((sg.type_dict[trip[0]],trip[1],sg.type_dict[trip[2]]))
    return SchemaGraph
num_ents = len(schemaTrips)
with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            f1 = executor.submit(SchemaCreator,0,num_ents//4)
            f2 = executor.submit(SchemaCreator,num_ents//4,num_ents//2)
            f3 = executor.submit(SchemaCreator,num_ents//2 ,3*(num_ents//4))
            f4 = executor.submit(SchemaCreator,3*(num_ents//4),num_ents)
            while (f1.done() and f2.done() and f3.done() and f4.done())==False:
                pass
            SchemaGraph = f1.result() + f2.result() + f3.result() + f4.result()
SchemaGraph = list(set(SchemaGraph))
pprint.pprint(SchemaGraph)
sample_graph['tags'] = t_p
t2 = time.time()


print("SchemaGenerator elapsed time :",t2-t1,"s")
# with open("pruned_sample_graph.json", "w") as outfile:
#     json.dump(sample_graph, outfile)
