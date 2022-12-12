from config import (config, LON_1, LAT_1, LON_2, LAT_2, MAP_NAME)
import osmnx as ox
import time


# osm_file = "osm_files/england-latest.osm.bz2"
osm_file = "osm_files/greater-london-latest.osm.bz2"
# graph_file = "maps/england.graphml"
graph_file = "maps/Greater_London.graphml"

ox.config(log_console=True)

t1 = time.time()
print("starting")

G = ox.graph_from_xml(osm_file)
t2 = time.time()
print(f"loaded file: {t2 - t1}")

G = ox.add_edge_speeds(G)
t3 = time.time()
print(f"added edge speeds: {t3 - t2}")

G = ox.add_edge_travel_times(G)
t4 = time.time()
print(f"added travel times: {t4 - t3}")

ox.save_graphml(G, graph_file)
t5 = time.time()
print(f"saved: {t5 - t4}")

fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0,
                        edge_color='y', edge_linewidth=0.2)
t6 = time.time()
print(f"saved: {t6 - t5}")
print(f"total: {t6 - t1}")
