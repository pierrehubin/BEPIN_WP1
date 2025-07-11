# -*- coding: utf-8 -*-
"""

Project name: BE-PIN task 1.3 (WP1)

Script Name: inventory_graph

Short Description: Export fields from JSON inventory to gephi format for graph representation

Author: Pierre Hubin

Versioning:
v1 Creation Feb 18 2025 Pierre Hubin

"""

### Parameters for graph definition
# Attribute based on which edges are should be computed
edge_attribute = "relatedInfoNeed"
# Filtering boolean and list on which to filter
filtering = False
filtering_dict = {"relatedScenario":["R1"]}
filtering_key = "relatedScenario"
filtering_values = ["R1"]

### import modules
import sys
import os
import pandas as pd
import json
import csv
import networkx as nx
import matplotlib as mplot

### Define paths
path_to_folder = "//define/path/here/"
path_to_code = path_to_folder + "py"
inventory_file = path_to_folder + "metadata/data_sources.json"
graph_file = path_to_folder + "graph/graph_data_sources.gexf"

### import custom functions
sys.path.insert(0, path_to_code)
import helper_functions as hf

### Read the JSON file
with open(inventory_file, 'r') as f:
    inventory_data = json.load(f)
f.close()

### Create graph from inventory data (datasets = nodes)
nodes = list(inventory_data['datasets'])
if filtering:  # subset nodes based 
    nodes = [d for d in nodes if any(val in d.get(filtering_key, []) for val in filtering_values)]
    
# Create an empty graph
G = nx.Graph()
# Add nodes along with their attributes to the graph
for node in nodes:
    #node_id = node.pop("id")
    G.add_node(node["id"], **node)


# Create an empty list to store the edges
edges = []
weights = []
sizes = []

# Iterate over the nodes
for i in range(len(nodes)):
    sizes.append(len(nodes[i][edge_attribute]))
    for j in range(i+1, len(nodes)):
        # If the attribute value is the same, add a tuple of the ids to the edges list
        if set(nodes[i][edge_attribute]).intersection(nodes[j][edge_attribute]):
            edges.append((nodes[i]["id"], nodes[j]["id"]))
            common_elements = set(nodes[i][edge_attribute]).intersection(nodes[j][edge_attribute])
            weights.append(len(common_elements))

sizes_dict = {index: value for index, value in enumerate(sizes)}
nx.set_node_attributes(G, sizes_dict, name="size")

# Now edges is a list of tuples representing the edges between nodes with the same attribute value
print(edges)
for i in range(len(edges)):
    G.add_edge(edges[i][0],edges[i][1],weight=weights[i])
# G.add_weighted_edges_from(edges,weights)
# Remove self-loops
G.remove_edges_from(nx.selfloop_edges(G))
    
### Visualize data with simple graph (colored by format)
# Color nodes based on attribute
color_map = []
for i in range(1,len(G)+1):
    if G.nodes[i]['accessibility'] == "opendata":
        color_map.append('green')
    else: 
        color_map.append('grey') 
# Get the labels
labels = nx.get_node_attributes(G, 'name')
# Draw the graph      
nx.draw(G, node_color=color_map, with_labels=True, labels=labels)
# Display the graph
mplot.pyplot.show()    


### Output in Gephy format to create customizable graphs
# Define the list of attributes you want to keep
attributes_to_keep = ['name','size']
# Select a subset of node attributes
subset_info = {node: {attr: data[attr] for attr in attributes_to_keep if attr in data} 
               for node, data in G.nodes(data=True)}
# Create a new graph H
H = nx.Graph()
# Add nodes to H with the subset of attributes
for node, data in subset_info.items():
    H.add_node(node, **data)
# Add edges to H (assuming edge attributes are not needed)
for i in range(len(edges)):
    H.add_edge(edges[i][0],edges[i][1],weight=weights[i])
H.remove_edges_from(nx.selfloop_edges(H))
nx.write_gexf(H, graph_file)





