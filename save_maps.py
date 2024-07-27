import osmnx as ox
import networkx as nx
from datetime import timedelta
from os.path import exists
import time
from config import NORTH, SOUTH, EAST, WEST, MAP_NAME


st = time.time()

ox.config(use_cache=True,
          log_console=True,
          #overpass_endpoint="https://overpass.kumi.systems/api/",
          overpass_endpoint="http://overpass-api.de/api",
          # overpass_endpoint="https://z.overpass-api.de/api",
         )

# The place where your 2 points are located. It will be used to create a graph from the OSM data
# It could be a bounding box too, or an area around a point

graph_file = f"maps/{MAP_NAME}.graphml"
if exists(graph_file):
    print(f"mapfile {graph_file} exists")
    exit(0)

print(f"Creating mapfile {graph_file}")
# Create the graph of the area from OSM data.
# It will download the data and create the graph

G = ox.graph_from_bbox(NORTH, SOUTH, EAST, WEST, network_type='walk')

# G = ox.graph_from_place(graph_area, network_type='walk')

# OSM data are sometime incomplete so we use the speed module of osmnx
# to add missing edge speeds and travel times
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# Save graph to disk if you want to reuse it
ox.save_graphml(G, graph_file)

# Plot the graph
fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0,
                        edge_color='y', edge_linewidth=0.2)

et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')
