#!/usr/bin/python
import csv
import psycopg2
from config import config
import time
from math import sin, cos, sqrt, atan2, radians
import itertools
import osmnx as ox
import networkx as nx
from os.path import exists

def process_walking():
    """ query data from the vendors table """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""
                    SELECT d.id, l_a.lat as start_lat, l_a.lon as start_lon,
                            l_b.lat as end_lat, l_b.lon as end_lon
                    FROM location l_a, location l_b, distance d
                    WHERE l_a.pub_id = d.start_loc
                    AND l_b.pub_id = d.end_loc
                    """)
        distances = cur.fetchall()
        print("got distances")

        graph_file = "maps/London.graphml"
        if exists(graph_file):
            print("Loading mapfile")
            st = time.time()
            G = ox.load_graphml(graph_file)
            et = time.time()
            print("Map Loaded", int(et - st), " secs")

        distance_sql = """UPDATE distance SET walking_distance = %s WHERE id = %s"""

        count = 0
        added = 0
        for dist in distances:
            count += 1
            # (1, 51.958698, 1.057832, 51.975311, 1.05611)
            dist_id = dist[0]
            origin_coordinates = (dist[1], dist[2])
            destination_coordinates = (dist[3], dist[4])

            # origin_node = ox.get_nearest_node(G, origin_coordinates)
            # destination_node = ox.get_nearest_node(G, destination_coordinates)
            print(G)
            print(origin_coordinates[0], origin_coordinates[1])
            print(destination_coordinates[0], destination_coordinates[1])

            # find the nearest node to the start location
            orig_node = ox.nearest_nodes(G, origin_coordinates[1], origin_coordinates[0])# find the nearest node to the end location
            dest_node = ox.nearest_nodes(G, destination_coordinates[1], destination_coordinates[0])#  find the shortest path
            print(orig_node)
            print(dest_node)
            shortest_route = nx.shortest_path(G, orig_node, dest_node, method='bellman-ford')
            print(shortest_route)

            if origin_node != destination_node:
                added += 1
                distance_in_meters = nx.shortest_path_length(
                    G, origin_node, destination_node, weight='length')
                print(f"{distance_in_meters} metres")
                break
                cur.execute(distance_sql, (int(distance_in_meters), dist_id))
                print(distance_sql % (distance_in_meters, dist_id))

        print(f"{count} scanned, {added} added.")
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

if __name__ == '__main__':
    t1_start = time.process_time()

    process_walking()

    t1_stop = time.process_time()
    print("time taken: :", t1_stop-t1_start)


