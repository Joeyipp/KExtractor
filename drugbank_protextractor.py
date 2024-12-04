import os
import csv
import gzip
import collections
import re
import io
import networkx as nx
import matplotlib.pyplot as plt
import json
import xml.etree.ElementTree as ET
import pprint

import requests
import pandas

def prot_rows():

    with open("full_database.xml") as xml_file:
        tree = ET.parse(xml_file)
    root = tree.getroot()



    ns = '{http://www.drugbank.ca}'
    inchikey_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChIKey']/{ns}value"
    inchi_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChI']/{ns}value"

    protein_rows = list()
    for i, drug in enumerate(root):
        drugbank_id = drug.findtext(ns + "drugbank-id[@primary='true']")
        for category in ['target', 'enzyme', 'carrier', 'transporter']:
            proteins = drug.findall('{ns}{cat}s/{ns}{cat}'.format(ns=ns, cat=category))
            for protein in proteins:
                row = {'drugbank_id': drugbank_id, 'category': category}
                row['organism'] = protein.findtext('{}organism'.format(ns))
                row['known_action'] = protein.findtext('{}known-action'.format(ns))
                actions = protein.findall('{ns}actions/{ns}action'.format(ns=ns))
                row['actions'] = '|'.join(action.text for action in actions)
                uniprot_ids = [polypep.text for polypep in protein.findall(
                    "{ns}polypeptide/{ns}external-identifiers/{ns}external-identifier[{ns}resource='UniProtKB']/{ns}identifier".format(ns=ns))]         
                uniprot_name = [polypep.text for polypep in protein.findall(
                    "{ns}polypeptide/{ns}external-identifiers/{ns}external-identifier[{ns}resource='UniProt Accession']/{ns}identifier".format(ns=ns))]       
                if len(uniprot_ids) != 1:
                    continue
                if len(uniprot_name) != 1:
                    continue
                row['uniprot_id'] = uniprot_ids[0]
                row['uniprot_name'] = uniprot_name[0]
                ref_text = protein.findtext("{ns}references[@format='textile']".format(ns=ns))
                # pmids = re.findall(r'pubmed/([0-9]+)', ref_text)
                # row['pubmed_ids'] = '|'.join(pmids)
                protein_rows.append(row)

    protein_df = pandas.DataFrame.from_dict(protein_rows)
    return protein_df


# with open("full_database.xml") as xml_file:
#     tree = ET.parse(xml_file)
# protein_df = prot_rows(tree)
# rdf_triples = []
# ind = 0
# for row in protein_df.itertuples():
#     rdf_triples.append((protein_df['drugbank_id'][ind],protein_df['category'][ind],protein_df['uniprot_id'][ind]))
#     rdf_triples.append((protein_df['uniprot_id'][ind],'organism',protein_df['organism'][ind]))
#     rdf_triples.append((protein_df['uniprot_id'][ind],'actions',protein_df['actions'][ind]))
#     ind += 1
# def printGraph(triples):
#     G = nx.Graph()
#     for triple in triples:
#         G.add_node(triple[0])
#         G.add_node(triple[2])
#         G.add_edge(triple[0], triple[2])
        
#     pos = nx.spring_layout(G)
#     plt.figure(figsize=(12, 8))
#     nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
#             node_size=500, node_color='skyblue', alpha=0.9,
#             labels={node: node for node in G.nodes()})
#     nx.draw_networkx_edge_labels(G, pos,edge_labels = {(triple[0], triple[2]): triple[1]},font_color='red')
#     plt.axis('off')
#     plt.show()
# printGraph(rdf_triples[:20])