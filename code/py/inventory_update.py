# -*- coding: utf-8 -*-
"""

Project name: BE-PIN task 1.3 (WP1)

Script Name: inventory_update

Short Description: Update the JSON metadata file

Author: Pierre Hubin

Versioning:
v1 Creation Feb 13 2025 Pierre Hubin

"""

### Short description of the update
update_descr = "Adding datasets after consolidation with WP-2 litterature review"

### Need for an update of the info needs labels (True/False)
infoneeds_update = False

### import modules
import sys
import os
import datetime
import pandas as pd
import json
import csv

### Define paths and filenames
path_to_folder = "//define/path/here/"
path_to_code = path_to_folder + "py"
mod_file = path_to_folder + "metadata/data_sources_mod.json"
raw_file = path_to_folder + "metadata/data_sources_raw.json"
out_file = path_to_folder + "metadata/data_sources.json"

### import custom functions
sys.path.insert(0, path_to_code)
import helper_functions as hf

### Read the JSON file (work version)
with open(mod_file, 'r') as f:
    inventory_data = json.load(f)
f.close()
# backup the work version in "raw" file
with open(raw_file, 'w') as f:
    json.dump(inventory_data, f, indent=2)
f.close()

### Make backup of last consolidated version
with open(out_file, 'r') as f:
    inventory_cleaned = json.load(f)
f.close()
# Get previous version of the inventory db
current_version = str(len(inventory_cleaned['updates'])-1)
# define backup path
backup_file = path_to_folder + "metadata/backup/data_sources_" + current_version + ".json"
# make backup
with open(backup_file, 'w') as f:
    json.dump(inventory_cleaned, f, indent=2)
f.close()

### Incrmeent the updates part of the json
new_update = {"updateId": len(inventory_data['updates']),
              "updateDatetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              "updateDescription": update_descr}
inventory_data['updates'].append(new_update)

### Write the updated data back to the JSON file
with open(out_file, 'w') as f:
    json.dump(inventory_data, f, indent=2)
f.close()
# also update the tmp file
with open(mod_file, 'w') as f:
    json.dump(inventory_data, f, indent=2)
f.close()


### TODO

## update list of info needs
# if infoneeds_update:
    
## Check structure of the JSON file (existing fields,...) and correct
# fill missing keys with empty values
# required_keys = ['id','name','shortDescription','format','service',
#                  'team','dataCollectionMethod','physicalLocation','nrecords',
#                  'confidentialityLevel','source','updateFrequency','controllers',
#                  'contacts','projects','parents',
#                  'children','series','variables'] 
# inventory_data['datasets'] = hf.check_and_insert_keys(inventory_data['datasets'],
#                                                       required_keys)