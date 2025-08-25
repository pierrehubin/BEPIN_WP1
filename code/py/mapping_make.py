# -*- coding: utf-8 -*-
"""

Project name: BE-PIN task 1.3 (WP1)

Script Name: mapping_make

Short Description: Make the JSON mapping file

Author: Pierre Hubin

Versioning:
v1  Creation July 11 2025 Pierre Hubin
v2  Fix formatting output August 08 2025 Pierre Hubin
v3  Fix mapping info and data needs August 20 2025 Pierre Hubin

"""


### import modules
import sys
import pandas as pd
import json


### Define paths and filenames
path_to_folder = "//define/path/here/"
path_to_code = path_to_folder + "py"
xlsx_file = path_to_folder + "T1.1.Table_16062025_finalPRESurvey_2.xlsx"
datasources_file = path_to_folder + "metadata/data_sources.json"
out_file = path_to_folder + "metadata/bepin_WP1_structure.json"


### import custom functions
sys.path.insert(0, path_to_code)
import helper_functions as hf


### Import data from excel 
objectives = pd.read_excel(xlsx_file,'List Decisions').fillna("")
infoneeds = pd.read_excel(xlsx_file,'List Informations').fillna("")
dataneeds = pd.read_excel(xlsx_file,'List Data').fillna("") 
objectives_infoneeds = pd.read_excel(xlsx_file,'Links Decisions-Informations').fillna("")
infoneeds_dataneeds = pd.read_excel(xlsx_file,'Links Informations-Data').fillna("")
phases = pd.read_excel(xlsx_file,'Overall links').fillna("") 


### Import data from data sources json
with open(datasources_file, 'r') as f:
    datasources = json.load(f)
f.close()
# import id and names of datasets from other json
keys = ['id','name']
datasets_dict = hf.subset_keys_in_list(datasources['datasets'], keys)
for item in datasets_dict:
    if 'id' in item and isinstance(item['id'], int):
        item['id'] = f"DS{item['id']:03}"


### Make one list of dictionnary for each item

## objectives
objectives_dict = objectives.to_dict(orient='records')
objectives_infoneeds_dict = objectives_infoneeds.to_dict(orient='records')
# Clean the values and rename keys
chars_to_remove = "\n"
key_to_clean = "DECISION MAKING OBJECTIVES"
for item in objectives_infoneeds_dict:
    if key_to_clean in item and isinstance(item[key_to_clean], str):
        for char in chars_to_remove:
            item[key_to_clean] = item[key_to_clean].replace(char, "")
    if 'DECISION MAKING OBJECTIVES' in item:
         item['id'] = item.pop('DECISION MAKING OBJECTIVES')
for item in objectives_dict:
    if 'CODE' in item:
        item['id'] = item.pop('CODE')
    if 'DECISION MAKING OBJECTIVES' in item:
        item['name'] = item.pop('DECISION MAKING OBJECTIVES')
# Add topic based on id
for item in objectives_dict:
    first_char = item["id"][0]
    if first_char == "S":
        item["topic"] = "Surveillance and monitoring"
    elif first_char == "C":
        item["topic"] = "Clinical and medical aspects"
    elif first_char == "P":
        item["topic"] = "Prevention and control"
    else:
        item["topic"] = "unknown"
# Combine the two list of dictionnaries based on id 
# Create a lookup dictionary from the relations list
relation_lookup = {item["id"]: item["LINKED INFORMATION NEEDS"] for item in objectives_infoneeds_dict}
# Update each dictionary in main_list with the corresponding relation
for item in objectives_dict:
    item["relatedInfoNeeds"] = relation_lookup.get(item["id"], "") 
# Add phase information 
# first clean phases (keeo only first three characteres DECISION MAKING OBJETIVES and PANDEMIC/OUTBREAK PHASE)
keys = ['DECISION MAKING OBJECTIVES','PANDEMIC/OUTBREAK PHASE']
subsetted_phases = hf.subset_keys_in_list(phases.to_dict(orient='records'), keys)
for item in subsetted_phases:
    if 'DECISION MAKING OBJECTIVES' in item:
         item['id'] = item.pop('DECISION MAKING OBJECTIVES')
    if "id" in item and isinstance(item["id"], str):
        item["id"] = item["id"][:3]
phases_lookup = {item["id"]: item["PANDEMIC/OUTBREAK PHASE"] for item in subsetted_phases}
for item in objectives_dict:
    item["phase"] = phases_lookup.get(item["id"], "")
    # Convert string containing links to array of strings (one link by string)
    if 'relatedInfoNeeds' in item and isinstance(item['relatedInfoNeeds'], str):
        item['relatedInfoNeeds'] = [link.strip() for link in item['relatedInfoNeeds'].split(',')]
    # Reformat info needs list of ids
    item['relatedInfoNeeds'] = hf.standardize_ids(item['relatedInfoNeeds'])
desired_order = ["id", "name", "topic", "relatedInfoNeeds", "phase"]
objectives_dict = [
    {key: item[key] for key in desired_order if key in item}
    for item in objectives_dict
]

## info needs
infoneeds_dict = infoneeds.to_dict(orient='records')
infoneeds_dataneeds_dict = infoneeds_dataneeds.to_dict(orient='records')
for item in infoneeds_dict:
    if 'CODE' in item:
        item['id'] = item.pop('CODE')
    if 'INFORMATION NEEDS' in item:
        item['name'] = item.pop('INFORMATION NEEDS')
    # Add weight and availabiltiy (with default values)
    for item in infoneeds_dict:
        item['weight'] = 1
        item['availability'] = ""
for item in infoneeds_dataneeds_dict:
    if 'INFORMATION NEEDS' in item:
         item['id'] = hf.standardize_ids(item.pop('INFORMATION NEEDS'))
# Combine the two list of dictionnaries based on id 
# Create a lookup dictionary from the relations list
relation_lookup = {item["id"]: item["LINKED DATA NEEDS"] for item in infoneeds_dataneeds_dict}
# Update each dictionary in main_list with the corresponding relation
for item in infoneeds_dict:
    # Reformat info needs list of ids
    item['id'] = hf.standardize_ids(item['id'])
    item["relatedDataNeeds"] = relation_lookup.get(item["id"], "")
# Convert string containing links to array of strings (one link by string)
for item in infoneeds_dict:
    if 'relatedDataNeeds' in item and isinstance(item['relatedDataNeeds'], str):
        item['relatedDataNeeds'] = [link.strip() for link in item['relatedDataNeeds'].split(',')]
        item['relatedDataNeeds'] = hf.standardize_ids(item['relatedDataNeeds'])
desired_order = ["id", "name", "weight", "availability", "relatedDataNeeds"]
infoneeds_dict = [
    {key: item[key] for key in desired_order if key in item}
    for item in infoneeds_dict
]

## data needs
dataneeds_dict = dataneeds.to_dict(orient='records')
for item in dataneeds_dict:
    if 'CODE' in item:
        item['id'] = item.pop('CODE')
    if 'DATA NEEDS' in item:
        item['name'] = item.pop('DATA NEEDS')
    # Reformat info needs list of ids    
    item['id'] = hf.standardize_ids(item['id'])
    item['relatedDatasets'] = []  # mapping to datasets to be added manually


### Combine all list of dictionnaries and export in json
output = {
    "objectives": objectives_dict,
    "infoneeds": infoneeds_dict,
    "dataneeds": dataneeds_dict,
    "datasets": datasets_dict
}
with open(out_file, 'w') as f:
    json.dump(output, f, indent=2)
f.close()

