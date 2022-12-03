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

def plot_path(start, end):
    if len(PATHS) == 0:  # we're starting the search - find a bounding box
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
        # pprint.pprint(PATHS)

    print("subsequent")
    # foreach starting point, plot the next point
    for idx, path in enumerate(PATHS):
        # find closest pubs
        last_element = len(path)-1
        location = path[last_element]

        # find closest pubs
        cur.execute(next_pubs_sql % (location[1], location[1]))
        next_pubs = cur.fetchall()
        # TODO - remove the puobs that take us further than the goal
        pprint.pprint(f" 1 {path} ")
        # pprint.pprint(f" 2 {next_pubs}")
        current_distance = get_distance(location[3], location[4], end_lat, end_lon)
        for sub_idx, next_pub in enumerate(next_pubs):
            if sub_idx == 10:
                break
            distance_to_target = get_distance(
                location[3], location[4],
                next_pub[3], next_pub[4]
            )
            print(current_distance, distance_to_target)
            print(sub_idx, location[3], location[4], next_pub[0], next_pub[3], next_pub[4])
        break
    print("z")


if __name__ == '__main__':
    t1_start = process_time()

    # collect coordinates
    start = input("starting coordinates (lat, long): ")
    if "," not in start:
        start = "51.5007169,-0.1847102"
    start_lat, start_lon = start.split(',')
    try:
        start_lat = float(start_lat)
        start_lon = float(start_lon)
    except Exception as e:
        print(e)
        exit()
    end = input("ending coordinates (lat, long): ")
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

        plot_path((start_lat, start_lon), (end_lat, end_lon))

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    t1_stop = process_time()
    print("time taken: :", t1_stop-t1_start)


