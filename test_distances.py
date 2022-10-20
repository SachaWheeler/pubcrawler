import osmnx as ox
import networkx as nx
from datetime import timedelta
from os.path import exists


# The place where your 2 points are located. It will be used to create a graph from the OSM data
# In this example, the 2 points are two addresses in Manhattan, so we choose "Manhattan"
# It could be a bounding box too, or an area around a point
graph_area = ("London, England, UK")

graph_file = "London.graphml"
if not exists(graph_file):

    # Create the graph of the area from OSM data. It will download the data and create the graph
    G = ox.graph_from_place(graph_area, network_type='walk')

    # OSM data are sometime incomplete so we use the speed module of osmnx to add missing edge speeds and travel times
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    # Save graph to disk if you want to reuse it
    ox.save_graphml(G, graph_file)
else:

    # Load the graph
    G = ox.load_graphml(graph_file)

# Plot the graph
# fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0, edge_color='y', edge_linewidth=0.2)

# Two pairs of (lat,lng) coordinates
origin_coordinates = (51.501888, -0.190900)
destination_coordinates = (51.486200, -0.165340)

# If you want to take an address (osmx will use Nominatim service for this)
# origin_coordinates = ox.geocode("2 Broad St, New York, NY 10005")

# In the graph, get the nodes closest to the points
origin_node = ox.get_nearest_node(G, origin_coordinates)
destination_node = ox.get_nearest_node(G, destination_coordinates)

# Get the distance in meters
distance_in_meters = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
print(distance_in_meters)
