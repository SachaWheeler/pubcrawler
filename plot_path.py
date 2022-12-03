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
    # find bounding box for first pub - 1000m
    if start[0] < end[0]:  # going north
        south_bound = start[0]
        north_bound = start[0] + KM_TO_DEGREES
    else:  # going south
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
        distance = get_distance(start[0], start[1], pub[3], pub[4])
        addition = pub + (distance,)
        PATHS.append([addition])
    PATHS.sort(key=lambda array_tup: array_tup[0][5])  # sorts in place

def plot_next_steps(start, end):  # ((pub tuple), (end_lat, end_lon))
    # find closest pubs
    # pprint.pprint(start)
    cur.execute(next_pubs_sql % (start[1], start[1]))
    next_pubs = cur.fetchall()

    current_distance = get_distance(start[3], start[4], end[0], end[1])
    next_count = 0
    next_steps = []
    for sub_idx, next_pub in enumerate(next_pubs):
        pub_distance_to_target = get_distance(
            next_pub[3], next_pub[4],
            end[0], end[1]
        )
        if current_distance - pub_distance_to_target <= 0:
            # if further away from target
            continue
        next_count += 1
        next_steps.append(next_pub)
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

    PATHS = []
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        starting_points((start_lat, start_lon), (end_lat, end_lon))

        for idx, pub in enumerate(PATHS):
            next_pub = pub[-1]
            pprint.pprint(pub)
            pprint.pprint(next_pub)
            print("xx")

            next_paths = plot_next_steps(
                next_pub, (end_lat, end_lon)
            )
            pprint.pprint(next_paths)
            PATHS[idx][-1].append(next_paths)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    t1_stop = process_time()
    print("time taken: :", t1_stop-t1_start)


