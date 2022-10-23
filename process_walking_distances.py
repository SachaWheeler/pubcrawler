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


def output(count, added, deleted):
    print(f"{count} scanned, {deleted} deleted, {added} added.")

def process_walking():
    """ query data from the vendors table """
    conn = None
    count = 0
    added = 0
    deleted = 0
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # london bounding box - http://bboxfinder.com/
        # -0.225157,51.439503,-0.086454,51.550010
        lon1, lat1, lon2, lat2 = -0.225157,51.439503,-0.086454,51.550010
        st = time.time()
        cur.execute(f"""
                    SELECT d.id, l_a.lat as start_lat, l_a.lon as start_lon,
                            l_b.lat as end_lat, l_b.lon as end_lon
                    FROM location l_a, location l_b, distance d
                    WHERE l_a.pub_id = d.start_loc
                    AND l_b.pub_id = d.end_loc

                    AND (l_a.lon BETWEEN {lon1} AND {lon2})
                    AND (l_a.lat BETWEEN {lat1} AND {lat2})
                    AND (l_b.lon BETWEEN {lon1} AND {lon2})
                    AND (l_b.lat BETWEEN {lat1} AND {lat2})

                    AND d.walking_distance < 1
                    ORDER by d.distance

                    """)
        distances = cur.fetchall()
        et = time.time()
        print(f"got {len(distances)} distances in {int(et-st)} secs")

        graph_file = "maps/London_zoom.graphml"
        if exists(graph_file):
            print(f"Loading mapfile: {graph_file}")
            st = time.time()
            G = ox.load_graphml(graph_file)
            et = time.time()
            print(G)
            print("Map Loaded", int(et - st), "secs")

        distance_sql = """UPDATE distance SET walking_distance = %s WHERE id = %s"""
        distance_delete_sql = """DELETE FROM distance WHERE id = %s"""

        dist_iter = iter(distances)
        for dist in dist_iter:
            if count ==0:
                print("started the loop")
            elif count%100==0:
                output(count, added, deleted)
            count += 1
            # (1, 51.958698, 1.057832, 51.975311, 1.05611)
            dist_id = dist[0]
            orig_coords = (dist[1], dist[2])
            dest_coords = (dist[3], dist[4])

            # find the nearest node to the start location. LON, LAT (X, Y), not LAT, LON
            orig_node = ox.nearest_nodes(G, orig_coords[1], orig_coords[0])# find the nearest node to the end location
            dest_node = ox.nearest_nodes(G, dest_coords[1], dest_coords[0])#  find the shortest path

            # shortest_route = nx.shortest_path(G, orig_node, dest_node, method='bellman-ford')

            if orig_node == dest_node:
                cur.execute(distance_delete_sql, (dist_id,))
                deleted += 1
            else:
                added += 1
                distance_in_meters = nx.shortest_path_length(
                    G, orig_node, dest_node, weight='length')
                print(orig_coords, dest_coords, f"{int(distance_in_meters)} metres")
                # break
                cur.execute(distance_sql, (int(distance_in_meters), dist_id))
            next(dist_iter)

        output(count, added, deleted)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
        output(count, added, deleted)

if __name__ == '__main__':
    t1_start = time.process_time()

    process_walking()

    t1_stop = time.process_time()
    print("time taken: :", t1_stop-t1_start)


