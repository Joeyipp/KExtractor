# Knowledge Enrichment Pipeline


## Introduction
This pipeline performs Knowledge Enrichment on biomedical entities that have been extracted. It's an end-to-end pipeline that takes a text file containing the entities as input and produces two files: the triples created and the graph's schema. 

## Requirements
Create a seperate python environment to use the code. The python version is 3.7.11. Important modules are listed below.

- Wikidata 0.7.0
- spacy-dbpedia-spotlight 0.2.1
- pydbpedia 0.0.3
- flair 0.10
- rdflib 6.1.1

Entry point: run_KExtractor.py

## Pipeline Architecture
![Pipeline](/Images/pipeline.PNG)

## Entity Linking
- [Spacy DBpedia spotlight](https://pypi.org/project/spacy-dbpedia-spotlight/) linker is used for the task.
- Performed by the *dbpedia_linker.py* script.

## DBpedia Extraction
- Performed by the *dbpedia_extractor.py* script.
- Using the [rdflib](https://github.com/RDFLib/rdflib) it extracts DBpedia knowledge.
- The owl#sameAs predicate provides the corresponding Wikidata and Drugbank identifiers of the entity.

## Wikidata Extraction
- Performed by the *wikidata_extractor.py* script.
- Wikidata uses entity and property identifiers to represent the graph, therefore a dictionary containing the identifier-name correspondancy is created.
- Wikidata has a number of external links that can be used to extract more knowledge if needed. 

## Drugbank Extraction
![Drugbank Sample Graph](/Images/Abarelix.png)
- Requires a Drugbank licence.
- Contains information on aliases, categories, targets, enzymes etc.
- Performed by *drugbank_extractor.py*. 

## Schema Generation
- Due to the different Knowledge graphs that are being integrated, external tagging is used to generate the schema.
- Performed by *tagger.py* using [HunFlair](https://github.com/flairNLP/flair/blob/master/resources/docs/HUNFLAIR.md) biomedical tagger.
- The tagger uses the triples.txt file generated by the enrichment step as input, and the nodes and labels are saved in the form of a dictionary (tag_dict.json) after they've been tagged. 
![Sample Schema](/Images/ss.png)



## External References

- [DBpedia](https://www.dbpedia.org)
- [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page)
- [Drugbank](https://go.drugbank.com/)
- [HunFlair](https://github.com/flairNLP/flair/blob/master/resources/docs/HUNFLAIR.md)




