#!/usr/bin/python
import csv
import psycopg2
from config import (config,
                    LON_1, LAT_1, LON_2, LAT_2,
                    MAP_NAME)
import time
from math import sin, cos, sqrt, atan2, radians
import itertools
import osmnx as ox
import networkx as nx
from os.path import exists


def output(count, added, skipped, time_taken):
    print(f"{count} scanned, {skipped} skipped, {added} added in {time_taken}.")

def load_map():
    graph_file = f"maps/{MAP_NAME}.graphml"
    if exists(graph_file):
        print(f"Loading mapfile: {graph_file}")
        st = time.time()
        G = ox.load_graphml(graph_file)
        et = time.time()
        print(G)
        print("Map Loaded", int(et - st), "secs")
        return G
    exit(0)

def process_walking():
    """ query data from the vendors table """
    conn = None
    count = 0
    added = 0
    skipped = 0

    closest_node = {}
    try:
        params = config()
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        st = time.time()
        cur.execute(f"""
                    SELECT d.id,
                        l_a.lat as start_lat, l_a.lon as start_lon,
                        l_b.lat as end_lat,   l_b.lon as end_lon,
                        d.distance
                    FROM location l_a, location l_b, distance d
                    WHERE l_a.pub_id = d.start_loc
                    AND l_b.pub_id = d.end_loc

                    AND (l_a.lon BETWEEN {LON_1} AND {LON_2})
                    AND (l_a.lat BETWEEN {LAT_1} AND {LAT_2})
                    AND (l_b.lon BETWEEN {LON_1} AND {LON_2})
                    AND (l_b.lat BETWEEN {LAT_1} AND {LAT_2})

                    AND d.walking_distance is null
                    ORDER by d.distance

                    """)

        distances = cur.fetchall()
        et = time.time()
        print(f"got {len(distances)} distances in {int(et-st)} secs")

        G = load_map()
        distance_sql = """UPDATE distance SET walking_distance = %s WHERE id = %s"""

        # dist_iter = iter(distances)
        prev_output_time = time.time()
        for dist in distances:
            if count ==0:
                print("started the loop")
            elif count%100==0:
                time_now = time.time()
                output(count, added, skipped, int(time_now - prev_output_time))
                prev_output_time = time_now
            count += 1
            # (1, 51.958698, 1.057832, 51.975311, 1.05611)
            dist_id = dist[0]
            orig_coords = (dist[1], dist[2])
            dest_coords = (dist[3], dist[4])

            # find the nearest node to the start location. LON, LAT (X, Y), not LAT, LON
            if orig_coords in closest_node:
                orig_node = closest_node[orig_coords]
            else:
                orig_node = ox.nearest_nodes(G, orig_coords[1], orig_coords[0])# find the nearest node to the end location
                closest_node[orig_coords] = orig_node
            if dest_coords in closest_node:
                dest_coords = closest_node[dest_coords]
            else:
                dest_node = ox.nearest_nodes(G, dest_coords[1], dest_coords[0])#  find the shortest path
                closest_node[dest_coords] = dest_node

            # shortest_route = nx.shortest_path(G, orig_node, dest_node, method='bellman-ford')

            if orig_node == dest_node:
                skipped += 1
                distance_in_meters = 0
            else:
                added += 1
                distance_in_meters = nx.shortest_path_length(
                    G, orig_node, dest_node, weight='length')
            cur.execute(distance_sql, (int(distance_in_meters), dist_id))

        output(count, added, skipped, time.time())
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
        output(count, added, skipped, time.process_time())

if __name__ == '__main__':
    t1_start = time.process_time()

    process_walking()

    t1_stop = time.process_time()
    print("time taken: :", t1_stop-t1_start)


