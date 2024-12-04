from dbpedia_extractor import dbpedia_extractor
from wikidata_extractor import wikidata_extractor
from dbpedia_linker import dbpedia_linker
from dbpedia_tagger import dbpedia_tagger
import json
import pprint, rdflib
import networkx as nx
import numpy as np
import pandas as pd
from urllib.error import HTTPError
import concurrent.futures
import spacy
from random import sample
from rdflib import Graph
import multiprocessing
import time
from time import process_time
from rdflib.plugin import register, Serializer
from ldtools.resource import Resource
from ldtools.origin import Origin
from drugbank_tool import DrugBank_tool
from spacy.util import filter_spans
import pickle
import re

# Function to align DBpedia and WikiData based on the sameAs predicate
def db_wiki_Align(d_uris,w_uris,start,end):
    for uri in d_uris:
        if 'http://dbpedia.org' in uri[start:end] :
        # uri.replace('https','http')
            try :
                origin, created = Origin.objects.get_or_create(uri)
                origin.GET(only_follow_uris=[rdflib.OWL.sameAs])
                resource, created = Resource.objects.get_or_create(uri, origin=origin)
                dicto = resource.__dict__
                for res in list(dicto['owl_sameAs']):
                    try :
                        if 'wikidata' in str(res._uri) and str(res._uri) in w_uris:
                            print(uri,'sameAs',str(res._uri))
                    except Exception:
                        pass
            except Exception :
                pass
            
def createGraph(rdf_triples):
    subject = []
    predicate = []
    object = []    
    for triple in rdf_triples :
        subject.append(triple[0])
        predicate.append(triple[1])
        object.append(triple[2])
        kg_df = pd.DataFrame({'subject':subject, 'object':object, 'predicate':predicate})
    G=nx.from_pandas_edgelist(kg_df, "subject", "object", edge_attr=True, create_using=nx.DiGraph())
    pos = nx.spring_layout(G)
    return G                               


class GraphConstructor():
    def __init__(self,filename):
        self.Node_data = {} 
        #self.dbtool = DrugBank_tool() # Declared Early to maintain efficiency wrt running time
        self.ent2uri = {}
        self.DBGraph = nx.DiGraph()
        self.WikiGraph = nx.DiGraph()
        self.DbankGraph = nx.DiGraph()
        self.ext = []
        # Receive input from text files
        with open(filename) as f:
            lines = f.read().splitlines() 
        self.entities = list(set(lines))
        with open('preds.txt') as file:
            lines = file.readlines()
            self.preds = [line.rstrip() for line in lines]
        
        #create instances of rdflib graph, spacy models and dbpedia spotlight for entity linking
        self.g = Graph()
        self.nlp = spacy.load('en_core_web_lg')
        self.nlp.add_pipe('dbpedia_spotlight')
    
    def run_tagger(self,uris,start,end):
        dicto = []
        #start and end are provided to facilitate multiprocessing, tags uri based on dbpedia rdf-syntaxtype predicate
        for uri in uris[start:end]:
            if 'http' in uri and 'http://dbpedia.org/resource/' in uri:
                name = uri.rsplit('/', 1)[-1]
                tagger = dbpedia_tagger(uri)
                dicto.append((name,uri,tagger.tags))
        return dicto

    def run_wikiExtractor(self,uris,start,end):
        #extracts triples from WikiData using the rdflib library
        triples = []
        for uri in uris[start:end]:
            print(uri)
            if uri != '':
                code = uri.rsplit('/', 1)[-1]
                w = wikidata_extractor(code,self.g,self.preds)
                w.triples_extractor()
                triples += w.triples
        return triples
    
    def run_dbankExtractor(self,ids,start,end,dbtool):
        #retrieves triples from drugbank knowledge base using the schema which is obtainable after procuring a licence
        triples = []
        for id in ids[start:end]:
            print(id+':')
            if id != '':
                # code = uri.rsplit('/', 1)[-1]
                dbtriples = dbtool.find_and_retrieve(id)
                triples += dbtriples
        return triples


    def run_linker(self,start,end):
        # Takes in a string and links it to a DBpedia URI and then extracts triples from DBpedia, in addition retrieves external links for DrugBank and WikiData
        sd = {}
        raw_trip = []
        dbank_ids = []
        wiki_identifiers = []

        for ent in self.entities[start:end]:
            try :
                print(ent)
                #link entities to DBpedia
                link = dbpedia_linker(ent,self.nlp,self.g)
                link.linker()
                uri = link.uri
                self.ent2uri[ent] = uri
                #extract triples from DBpedia
                db_tool = dbpedia_extractor(uri,self.g,self.preds)
                db_tool.triples_extractor()
                ext = db_tool.triples
                raw_trip+= ext
                nodes = []
                raw_trip = list(set(raw_trip))
                wlink = db_tool.wikiURI
                wiki_identifiers.append(wlink)
                db_id = db_tool.drugbankID
                dbank_ids.append(db_id)
            except Exception:
                pass

           
       
        # print("Triples:",self.raw_triples)
        return raw_trip,wiki_identifiers,dbank_ids
            
 
            
        
        
    def run_pipeline(self):
        self.raw_triples = []
        self.dbtrips = []
        self.wtrips = []
        self.dbanktrips = []
        tuples = []
        num_ents = len(self.entities)
        #DBpedia triples + WikiData URI's + DrugBank ID's extraction
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            f1 = executor.submit(self.run_linker,0,num_ents//4)
            f2 = executor.submit(self.run_linker,num_ents//4,num_ents//2)
            f3 = executor.submit(self.run_linker,num_ents//2 ,3*(num_ents//4))
            f4 = executor.submit(self.run_linker,3*(num_ents//4),num_ents)
            while (f1.done() and f2.done() and f3.done() and f4.done())==False:
                pass
            self.raw_triples = f1.result()[0] + f2.result()[0] + f3.result()[0] + f4.result()[0]
            self.wikiLinks = f1.result()[1] + f2.result()[1] + f3.result()[1] + f4.result()[1]
            self.dbank_ids = f1.result()[2] + f2.result()[2] + f3.result()[2] + f4.result()[2]

        self.wikiLinks = list(set(self.wikiLinks))
        self.dbank_ids = list(set(self.dbank_ids))
        num_ents = len(self.wikiLinks)
        num_dents = len(self.dbank_ids)
        print("Initialize drugbank")
        dbtool = DrugBank_tool()
        print(dbtool.protein_df.head())
        print("Complete")
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            f1 = executor.submit(self.run_wikiExtractor,self.wikiLinks,0,num_ents//3)
            f2 = executor.submit(self.run_wikiExtractor,self.wikiLinks,num_ents//3,2*num_ents//3)
            f3 = executor.submit(self.run_wikiExtractor,self.wikiLinks,2*num_ents//3,num_ents)
            while (f1.done() and f2.done() and f3.done())==False:
                pass
            self.raw_triples += f1.result() + f2.result() + f3.result() 
        
        print(self.dbank_ids)
        self.raw_triples+=self.run_dbankExtractor(self.dbank_ids,0,num_dents,dbtool)
        with open('triples.txt', 'w') as f:
            for line in self.raw_triples:
                f.write(str(line))
                f.write('\n')

        # wikidict = {}
        # uris = []
        # wuris = [] 
        # ind = 0
        # for trip in self.raw_triples:
        #     if trip[-1] == 'wikidata':
        #         if trip[1] in ["http://www.w3.org/2000/01/rdf-schema#label","http://www.w3.org/2004/02/skos/core#prefLabel"]:
        #             wikidict[trip[0].split('/')[-1]] = trip[2]
        #     if trip[1] == 'name':
        #             print(trip)
        #             wikidict[trip[0]] = trip[2]
        # # pprint.pprint(wikidict)
        # for trip in self.raw_triples:
        #     if trip[-1] == 'DBpedia':
        #         s = trip[0]
        #         p = trip[1]
        #         o = trip[2]
        #         if 'wikipedia' not in s and 'wikipedia' not in o:
        #             if o in wikidict.keys():
        #                 o = wikidict[o.split('/')[-1]]
        #             trip = (s,p,o,'DBpedia')
        #             if s !=o :
        #                 self.dbtrips.append(trip)
        #             uris.append(trip[0])
        #             uris.append(trip[2])
        #     elif trip[-1] == 'wikidata':
        #         s = trip[0]
        #         p = trip[1]
        #         o = trip[2]
        #         if 'wikipedia' not in s and 'wikipedia' not in o:
        #             if s in wikidict.keys():
        #                 s = wikidict[s.split('/')[-1]]
        #             if p in wikidict.keys():
        #                 p = wikidict[p.split('/')[-1]]
        #             if o in wikidict.keys():
        #                 o = wikidict[o.split('/')[-1]]
        #             trip = (s,p,o,'wikidata')
        #             if s!=o:
        #                 self.wtrips.append(trip)
        #             wuris.append(trip[0])
        #             wuris.append(trip[2])
        #     elif trip[-1] == 'Drugbank':
        #         if trip[0] in wikidict.keys():
        #             trip = (wikidict[trip[0]],trip[1],trip[2],'Drugbank')
        #         self.dbanktrips.append(trip)

        
 
        # self.DBGraph = createGraph(self.dbtrips)
        # self.WikiGraph = createGraph(self.wtrips)
        # self.DbankGraph = createGraph(self.dbanktrips)
       

        # pprint.pprint(self.DbankGraph.edges())
        # uris = list(set(uris))
        # wuris = list(set(wuris))
        # num_ents = len(uris)
        # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        #     f1 = executor.submit(db_wiki_Align,uris,wuris,0,num_ents//4)
        #     f2 = executor.submit(db_wiki_Align,uris,wuris,num_ents//4+1,num_ents//2)
        #     f3 = executor.submit(db_wiki_Align,uris,wuris,num_ents//2+1,3*(num_ents//4))
        #     f4 = executor.submit(db_wiki_Align,uris,wuris,3*(num_ents//4)+1,num_ents)
   
        




            


# t1_start = process_time() 
gc = GraphConstructor('sample.txt')
gc.run_pipeline()
# t1_stop = process_time()
# print("Elapsed time:", t1_stop, t1_start) 
   
# print("Elapsed time during the whole program in seconds:",
#                                          t1_stop-t1_start) 