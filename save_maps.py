import osmnx as ox
import networkx as nx
from datetime import timedelta
from os.path import exists
import time
from config import LON_1, LAT_1, LON_2, LAT_2


st = time.time()

# The place where your 2 points are located. It will be used to create a graph from the OSM data
# In this example, the 2 points are two addresses in Manhattan, so we choose "Manhattan"
# It could be a bounding box too, or an area around a point

graph_file = "maps/London_central.graphml"
if exists(graph_file):
    print(f"mapfile {graph_file} exists")
    exit(0)

print("Creating mapfile")
# Create the graph of the area from OSM data. It will download the data and create the graph
G = ox.graph_from_bbox(LON_1, LAT_1, LON_2, LAT_2, network_type='walk')

# G = ox.graph_from_place(graph_area, network_type='walk')

# OSM data are sometime incomplete so we use the speed module of osmnx to add missing edge speeds and travel times
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# Save graph to disk if you want to reuse it
ox.save_graphml(G, graph_file)

# Plot the graph
fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0, edge_color='y', edge_linewidth=0.2)

# Two pairs of (lat,lng) coordinates
et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')
