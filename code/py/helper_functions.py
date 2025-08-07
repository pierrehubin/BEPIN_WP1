# -*- coding: utf-8 -*-
"""

Project name: BE-PIN, WP1, task 1.3

Script Name: helper_function

Short Description: Definition of helper functions for other scripts of BE-PIN-WP1-task 1.3 project

Author: Pierre Hubin

Versioning:
v1  Adaptation for BE-PIN July 11 2025 Pierre Hubin
v2  Add standardize_ids function August 07 2025 Pierre Hubin  

"""

import csv

### Define functions
# Function to subset dictionaries in a list based on specified keys
def subset_keys_in_list(list_of_dicts, keys):
    subsetted_list = [{k: d[k] for k in keys if k in d} for d in list_of_dicts]
    return subsetted_list

# Function to check if a list of keys is present in a list of dictionnaries
# Add key with values if not present
# Order key-values in dictionnaries
def check_and_insert_keys(list_of_dicts, keys, default_value=None):
    for i in range(len(list_of_dicts)):
        for key in keys:
            if key not in list_of_dicts[i]:
                list_of_dicts[i][key] = default_value
        # Order each dictionary according to the list of keys
        list_of_dicts[i] = {key: list_of_dicts[i].get(key, default_value) for key in keys}
    return list_of_dicts

# Function to extract dictionnaries from a list based on given values of a selected key
def extract_elements(list_of_dicts, key, values):
    # Extract elements from the list of dictionaries based on the key-value pair
    extracted_elements = [d for d in list_of_dicts if d.get(key) in values]
    return extracted_elements

# Function to export the content of a list of dictionaries to a csv file
def export_to_csv(list_of_dicts, filename):
    # Export the list of dictionaries to a CSV file
    with open(filename, 'w', newline='') as csvfile:
        if list_of_dicts:
            fieldnames = list_of_dicts[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for d in list_of_dicts:
                d = {k: ', '.join(v) if isinstance(v, list) else v for k, v in d.items()}
                writer.writerow(d)
    csvfile.close()

# Function to rename keys in a list of dictionnaries based on a dictionnary "old_name": "new_name"
def rename_keys_in_list_of_dicts(list_of_dicts, key_mappings):
    for d in list_of_dicts:
        for old_key, new_key in key_mappings.items():
            if old_key in d:
                d[new_key] = d.pop(old_key)
    return list_of_dicts

# Function to standardize how ids are formatted
def standardize_ids(ids):
    def format_id(item):
        prefix = item[0].upper()      # Capitalize the prefix
        num = int(item[1:])           # Extract numeric part
        return f"{prefix}{num:03d}"   # Format with leading zeros

    if isinstance(ids, str):
        return format_id(ids)
    elif isinstance(ids, list):
        return [format_id(item) for item in ids]
    else:
        raise TypeError("Input must be a string or a list of strings")