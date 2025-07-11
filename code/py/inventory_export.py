# -*- coding: utf-8 -*-
"""

Project name: BE-PIN task 1.3 (WP1)

Script Name: inventory_export

Short Description: Export fields from JSON inventory to csv listing

Author: Pierre Hubin

Versioning:
v1 Creation Jan 08 2025 Pierre Hubin

"""

### import modules
import sys
import os
import pandas as pd
import json
import csv

### Define paths
path_to_folder = "//define/path/here/"
path_to_code = path_to_folder + "py"
inventory_file = path_to_folder + "metadata/data_sources.json"
listing_file = path_to_folder + "metadata/data_sources_listing.csv"


### import custom functions
sys.path.insert(0, path_to_code)
import helper_functions as hf


### Read the JSON file
with open(inventory_file, 'r') as f:
    inventory_data = json.load(f)
f.close()


### export listing
list_of_dicts = list(inventory_data['datasets'])

keys = ['id','name','institution','source','contactEmail','granularity',
        'accessibility','updateFrequency','sampleDescription','isPandemic',
        'isConventional','relatedScenario','relatedObjective','relatedInfoNeed']
subsetted_list = hf.subset_keys_in_list(list_of_dicts, keys)
hf.export_to_csv(subsetted_list, listing_file)

## If documents selection based on one key is needed
#key = 'institution'
#values = "Sciensano"
#extracted_elements = hf.extract_elements(list_of_dicts, key, values)
#
#subsetted_list = hf.subset_keys_in_list(extracted_elements, keys)
#hf.export_to_csv(subsetted_list, listing_file)



