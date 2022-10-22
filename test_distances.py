import osmnx as ox
import networkx as nx
from datetime import timedelta
from os.path import exists
import time


st = time.time()

# The place where your 2 points are located. It will be used to create a graph from the OSM data
# In this example, the 2 points are two addresses in Manhattan, so we choose "Manhattan"
# It could be a bounding box too, or an area around a point
graph_area = ("Royal Borough of Kensington and Chelsea, London, England, United Kingdom")

graph_file = "maps/K_and_C.graphml"
if exists(graph_file):

    print("Loading mapfile")
    # Load the graph
    G = ox.load_graphml(graph_file)

else:

    print("Creating mapfile")
    # Create the graph of the area from OSM data. It will download the data and create the graph
    G = ox.graph_from_place(graph_area, network_type='walk')

    # OSM data are sometime incomplete so we use the speed module of osmnx to add missing edge speeds and travel times
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    # Save graph to disk if you want to reuse it
    ox.save_graphml(G, graph_file)

# Plot the graph
fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0, edge_color='y', edge_linewidth=0.2)

# Two pairs of (lat,lng) coordinates
et = time.time()
print("Map Loaded")
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')
# devere gardens 51.4955399,-0.1818612
origin_coordinates = (51.4955399,-0.1818612)
# The Sporting Page 51.4846488,-0.1816031
destination_coordinates = (51.4846488,-0.1816031)

# If you want to take an address (osmx will use Nominatim service for this)
# origin_coordinates = ox.geocode("2 Broad St, New York, NY 10005")

# In the graph, get the nodes closest to the points
origin_node = ox.get_nearest_node(G, origin_coordinates)
# osmnx.distance.nearest_nodes(G, X, Y, return_dist=False)
# origin_node = ox.distance.nearest_nodes(G, origin_coordinates[0], origin_coordinates[1])
print(origin_node)
destination_node = ox.get_nearest_node(G, destination_coordinates)
# destination_node = ox.distance.nearest_nodes(G, destination_coordinates[0], destination_coordinates[1])
print(destination_node)

# Get the distance in meters
distance_in_meters = nx.shortest_path_length(G, origin_node,
                                             destination_node, weight='length')
print(distance_in_meters)

et = time.time()
elapsed_time = et - st
print('Total time:', elapsed_time, 'seconds')
