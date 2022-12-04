#!/usr/bin/python
import csv
import pprint
import psycopg2
from config import config
from time import process_time
from math import sin, cos, sqrt, atan2, radians
import itertools

from process_distances import get_distance
from process_walking_distances import load_map

from anytree import Node, RenderTree


class Pub:
    def __init__(self, id=None, name=None, address=None,
                 lat=None, lon=None, walking_distance=None):
        self.id = id
        self.name = name
        self.address = address
        self.lat = lat
        self.lon = lon
        self.walking_distance = walking_distance

    def __str__(self):
        return f"{self.name}, {self.address}"

    def __hash__(self):
        return hash((self.name, self.id))

    def __eq__(self, other):
        return (self.name, self.id) == (other.name, other.id)


def tuple_to_pub(pub_tuple=None):
    if pub_tuple is None:
        return None
    (name, id, address, lat, lon, walking_distance) = pub_tuple
    return Pub(
        id = id,
        name = name,
        address = address,
        lat = lat,
        lon = lon,
        walking_distance = walking_distance
    )

KM_TO_DEGREES = 0.00904
initial_pubs_sql ="""
    SELECT p.name, p.id, p.address, l.lat, l.lon
    FROM pub p, location l
    WHERE p.id = l.pub_id
    AND (l.lat BETWEEN %s AND %s)
    AND (l.lon BETWEEN %s AND %s)
    LIMIT 8
    """

next_pubs_sql ="""
select * from (
    SELECT p.name, p.id, p.address, l.lat, l.lon, d.walking_distance
    FROM pub p, location l, distance d
    WHERE p.id = d.end_loc
    AND l.pub_id = d.end_loc
    AND d.start_loc = %s

    UNION ALL

    SELECT p.name, p.id, p.address, l.lat, l.lon, d.walking_distance
    FROM pub p, location l, distance d
    WHERE p.id = d.start_loc
    AND l.pub_id = d.start_loc
    AND d.end_loc = %s
    ) t order by 6

    """

def starting_points(start, end):  # (start_lat, start_lon), (end_lat, end_lon))
    paths = []
    # find bounding box for first pub - 1000m
    if start[0] < end[0]:  # going north
        # print("north")
        south_bound = start[0]
        north_bound = start[0] + KM_TO_DEGREES
    else:  # going south
        # print("south")
        south_bound = start[0] - KM_TO_DEGREES
        north_bound = start[0]

    if start[1] < end[1]:  # going west
        east_bound = start[1]
        west_bound = start[1] + KM_TO_DEGREES
    else:  # going east
        east_bound = start[1] - KM_TO_DEGREES
        west_bound = start[1]

    # find closest 5 pubs to start point in the right direction
    cur.execute(initial_pubs_sql,
                (south_bound, north_bound,
                 east_bound, west_bound))

    start_pubs = cur.fetchall()
    # pprint.pprint(starting_pubs)
    for pub in start_pubs:
        # print(pub)
        # distance = get_distance(start[0], start[1], pub[3], pub[4])
        paths.append(pub)
    # paths.sort(key=lambda array_tup: array_tup[0][5])  # sorts in place
    return paths

def plot_next_steps(start, end):  # ((pub tuple), (end_lat, end_lon))
    # find closest pubs
    # pprint.pprint(start)
    cur.execute(next_pubs_sql % (start.id, start.id))
    next_pubs = cur.fetchall()

    current_distance = get_distance(start.lat, start.lon, end[0], end[1])
    next_count = 0
    next_steps = []
    for sub_idx, next_pub in enumerate(next_pubs):
        # pprint.pprint(next_pub)
        pub_obj = tuple_to_pub(next_pub)
        pub_distance_to_target = get_distance(
            pub_obj.lat, pub_obj.lon,
            end[0], end[1]
        )
        if current_distance - pub_distance_to_target <= 0:
            # if further away from target
            continue
        next_count += 1
        next_steps.append(pub_obj)
        if next_count == 5:
            break

    return next_steps


if __name__ == '__main__':
    t1_start = process_time()

    # collect coordinates
    start = ""  # input("starting coordinates (lat, long): ")
    if "," not in start:
        start = "51.5007169,-0.1847102"
    start_lat, start_lon = start.split(',')
    try:
        start_lat = float(start_lat)
        start_lon = float(start_lon)
    except Exception as e:
        print(e)
        exit()
    end = ""  # input("ending coordinates (lat, long): ")
    if "," not in end:
        end = "51.4516815,-0.1827658"
    end_lat, end_lon = end.split(',')
    try:
        end_lat = float(end_lat)
        end_lon = float(end_lon)
    except Exception as e:
        print(e)
        exit()

    # find distance between start and end
    total_dist = int(get_distance(start[0], start[1], end[0], end[1]))
    print(f" total distance: {total_dist}")

    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        pubcrawl = Node(f"({start_lat}, {start_lon}), ({end_lat}, {end_lon})")

        for pub in starting_points((start_lat, start_lon), (end_lat, end_lon)):
            dist = get_distance(start_lat, start_lon, pub[3], pub[4])
            pub_obj = tuple_to_pub(pub + (dist,))
            node = Node(pub_obj, parent=pubcrawl)

            for next_pub in plot_next_steps( pub_obj, (end_lat, end_lon)):
                Node(next_pub, parent=node)

        for pre, fill, node in RenderTree(pubcrawl):
            print("%s%s" % (pre, node.name))

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    t1_stop = process_time()
    print("time taken: :", t1_stop-t1_start)


