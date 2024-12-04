
import drugbank_extractor
import drugbank_protextractor
import datetime
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
class DrugBank_tool() :
    def __init__(self) :
        try:
            self.database = drugbank_extractor.drug_extractor()
            print("Drugbank N")
            self.protein_df = drugbank_protextractor.prot_rows()
            print("Drugbank Proteins")
            self.columns = self.database.columns
        except Exception:
            print("Drugbank Failure")
        
        
    
    def find_and_retrieve(self,dbid):
        triples = []
        for ind in range(len(self.protein_df)):
            if self.protein_df['drugbank_id'][ind] == dbid:
                triples.append((self.protein_df['drugbank_id'][ind],self.protein_df['category'][ind],self.protein_df['uniprot_name'][ind],'Drugbank'))
                triples.append((self.protein_df['uniprot_name'][ind],'organism',self.protein_df['organism'][ind],'Drugbank'))
                triples.append((self.protein_df['uniprot_name'][ind],'actions',self.protein_df['actions'][ind],'Drugbank'))
        for ind in range(len(self.database)):
            if self.database['drugbank_id'][ind] == dbid:
                for c in self.columns:
                    if type(self.database[c][ind]) == list :
                        for element in self.database[c][ind]:
                            triples.append((dbid,c,element,'Drugbank'))
                    elif type(self.database[c][ind]) == str :
                        triples.append((dbid,c,self.database[c][ind],'Drugbank'))
        
        return triples


                

# def createGraph(rdf_triples):
#     subject = []
#     predicate = []
#     object = []    
#     for triple in rdf_triples :
#         subject.append(triple[0])
#         predicate.append(triple[1])
#         object.append(triple[2])
#         kg_df = pd.DataFrame({'subject':subject, 'object':object, 'predicate':predicate})
#     G=nx.from_pandas_edgelist(kg_df, "subject", "object", edge_attr=True, create_using=nx.DiGraph())
#     plt.figure(figsize=(12,12))
#     pos = nx.spring_layout(G)
#     return G
#     # nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)
#     # nx.draw_networkx_edge_labels(G, pos=pos)
#     # plt.show()

        
# t = DrugBank_tool()
# rdf_triples = t.find_and_retrieve('DB00218')
# # def printGraph(triples):
# #     G = nx.DiGraph()
# #     for triple in triples:
# #         G.add_node(triple[0])
# #         G.add_node(triple[2])
# #         G.add_edge(triple[0], triple[2])
        
# #     pos = nx.spring_layout(G)
# #     plt.figure(figsize=(40, 40))
# #     nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
# #             node_size=500, node_color='skyblue', alpha=0.9,
# #             labels={node: node for node in G.nodes()})
# #     nx.draw_networkx_edge_labels(G, pos,edge_labels = {(triple[0], triple[2]): triple[1] for triple in triples},font_color='red')
# #     plt.axis('off')
# #     plt.show()

# createGraph(rdf_triples)