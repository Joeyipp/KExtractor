import xml.etree.ElementTree as ET
import collections
import pandas
# Passing the path of the
# xml document to enable the
# parsing process
def drug_extractor():
    tree = ET.parse('full_database.xml')
    # getting the parent tag of
    # the xml document
    root = tree.getroot()
    ns = '{http://www.drugbank.ca}'
    key_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChIKey']/{ns}value"
    key = "{ns}calculated-properties/{ns}property[{ns}kind='InChI']/{ns}value"

    rows = list()
    for i, drug in enumerate(root):
        row = collections.OrderedDict()
        assert drug.tag == ns + 'drug'
        row['type'] = drug.get('type')
        row['drugbank_id'] = drug.findtext(ns + "drugbank-id[@primary='true']")
        row['name'] = drug.findtext(ns + "name")
        row['description'] = drug.findtext(ns + "description")
        row['groups'] = [group.text for group in
            drug.findall("{ns}groups/{ns}group".format(ns = ns))]
        row['atc_codes'] = [code.get('code') for code in
            drug.findall("{ns}atc-codes/{ns}atc-code".format(ns = ns))]
        row['categories'] = [x.findtext(ns + 'category') for x in
            drug.findall("{ns}categories/{ns}category".format(ns = ns))]
        row['inchi'] = drug.findtext(key.format(ns = ns))
        row['inchikey'] = drug.findtext(key_template.format(ns = ns))
        row['brands'] = drug.findtext(ns+"international-brands")
        row['synonyms'] = [x.findtext(ns + 'synonym') for x in
            drug.findall("{ns}synonyms/{ns}synonym".format(ns = ns))]
        row['product'] = drug.findtext(ns+"products")
        # row['targets'] = [x.findtext(ns + 'target') for x in
        #     drug.findall("{ns}targets/{ns}target".format(ns = ns))]
        # Add drug aliases
        aliases = {
            elem.text for elem in 
            drug.findall("{ns}international-brands/{ns}international-brand".format(ns = ns)) +
            drug.findall("{ns}synonyms/{ns}synonym[@language='English']".format(ns = ns)) +
            drug.findall("{ns}international-brands/{ns}international-brand".format(ns = ns)) +
            drug.findall("{ns}products/{ns}product/{ns}name".format(ns = ns))

        }
        aliases.add(row['name'])
        row['aliases'] = sorted(aliases)

        rows.append(row)


    columns = ['drugbank_id', 'name', 'type', 'groups', 'atc_codes', 'categories','aliases']
    drugbank_df = pandas.DataFrame.from_dict(rows)[columns]
    return drugbank_df
# df = drug_extractor()
# print(df.head())