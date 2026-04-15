# -*- coding: utf-8 -*-
"""

Project name: BE-PIN task 1.3 (WP1)

Script Name: mapping_make

Short Description: Make the JSON mapping file

Author: Pierre Hubin

Versioning:
v1  Creation
    July 11 2025 Pierre Hubin
v2  Fix formatting output
    August 08 2025 Pierre Hubin
v3  Fix mapping info and data needs 
    August 20 2025 Pierre Hubin
v4  Add mapping data needs to datasets 
    move availability field to data needs instead of info need 
    fix script for v3 of excel input
    September 17 2025 Pierre Hubin
v5  Update to fit new excel structure
    March 24 2026 Pierre Hubin
v6  Simplify code after redefining data needs in the excel
    April 15 2026 Pierre Hubin

"""

### import modules
import sys
import pandas as pd
import json


### Define paths and filenames
path_to_folder = "//define/path/here/"
path_to_code = path_to_folder + "py"
xlsx_file = path_to_folder + "T13_preMapping_150426.xlsx"  # New excel modified, should contain all info
datasources_file = path_to_folder + "metadata/data_sources.json"
premapping_file = path_to_folder + "premapping_data.csv" 
out_file = path_to_folder + "metadata/bepin_WP1_structure.json"


### import custom functions
sys.path.insert(0, path_to_code)
import helper_functions as hf


### Import data from excel 
infoneeds = pd.read_excel(xlsx_file,'InfoNeeds').fillna("")
dataneeds = pd.read_excel(xlsx_file,'DataNeeds').fillna("") 
infoneeds_dataneeds = pd.read_excel(xlsx_file,'InfoData').fillna("")

### Import mapping data to datasets
dataneeds_datasets = pd.read_csv(premapping_file,sep=";")
dataneeds_datasets['Data_Code']=[f'D{i:03d}' for i in range(1, len(dataneeds_datasets)+1)]

### Import data from data sources json
with open(datasources_file, 'r') as f:
    datasources = json.load(f)
f.close()
# import id and names of datasets from other json
keys = ['id','name','detailLevel','accessibility','category']
datasets_dict = hf.subset_keys_in_list(datasources['datasets'], keys)
for item in datasets_dict:
    if 'id' in item and isinstance(item['id'], int):
        item['id'] = f"DS{item['id']:03}"


### Make one list of dictionnary for each item

## info needs
infoneeds_dict = infoneeds.to_dict(orient='records')

## data needs
dataneeds = dataneeds[['ID', 'Label', 'Description']]
dataneeds_dict = dataneeds.to_dict(orient='records')

## Combine info needs with data needs
infoneeds_dataneeds_dict = infoneeds_dataneeds.to_dict(orient='records')
# Combine the two list of dictionnaries based on id 
# Create a lookup dictionary from the relations list
relation_lookup = {item["InfoLabel"]: item["DataLabel"] for item in infoneeds_dataneeds_dict}
# Update each dictionary in main_list with the corresponding relation
for item in infoneeds_dict:
    # Reformat info needs list of ids
    item["relatedDataNeeds"] = relation_lookup.get(item["ID"], "")
# Convert string containing links to array of strings (one link by string)
for item in infoneeds_dict:
    if 'relatedDataNeeds' in item and isinstance(item['relatedDataNeeds'], str):
        item['relatedDataNeeds'] = [link.strip() for link in item['relatedDataNeeds'].split(',')]
        item['relatedDataNeeds'] = hf.standardize_ids(item['relatedDataNeeds'])
desired_order = ["ID", "Label", "Layer", "Domain", "Topic", "relatedDataNeeds"]
infoneeds_dict = [
    {key: item[key] for key in desired_order if key in item}
    for item in infoneeds_dict
]

## Combine dataneeds and datasets
dataneeds_datasets_dict = dataneeds_datasets.to_dict(orient='records')
for item in dataneeds_dict:
    if 'Data Code' in item:
        item['id'] = item.pop('Data Code')
    if 'Data Label' in item:
        item['name'] = item.pop('Data Label')
    item['relatedDatasets'] = [] 
for item in dataneeds_datasets_dict:
    if 'Data_Code' in item:
         item['id'] = hf.standardize_ids(item.pop('Data_Code'))
# Combine the two list of dictionnaries based on id 
# Create a lookup dictionary from the relations list
relation_lookup = {item["id"]: item["Datasets"] for item in dataneeds_datasets_dict}
# Update each dictionary in main_list with the corresponding relation
for item in dataneeds_dict:
    item["relatedDatasets"] = relation_lookup.get(item["ID"], "")
# Convert string containing links to array of strings (one link by string)
for item in dataneeds_dict:
    if 'relatedDatasets' in item and isinstance(item['relatedDatasets'], str):
        item['relatedDatasets'] = [link.strip() for link in item['relatedDatasets'].split(',')]
desired_order = ["ID", "Label", "Description", "relatedDatasets"]
dataneeds_dict = [
    {key: item[key] for key in desired_order if key in item}
    for item in dataneeds_dict
]


### Combine all list of dictionnaries and export in json
output = {
    "infoneeds": infoneeds_dict,
    "dataneeds": dataneeds_dict,
    "datasets": datasets_dict
}
with open(out_file, 'w') as f:
    json.dump(output, f, indent=2)
f.close()

# !!! TODO: 
# Add phases to info needs (--> first in excel)
# Uniformize keywords and notations