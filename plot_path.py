#!/usr/bin/python
import csv
import psycopg2
from config import config
from time import process_time
from math import sin, cos, sqrt, atan2, radians
import itertools

from process_distances import get_distance
from process_walking_distances import load_map

KM_TO_DEGREES = 0.00904

def plot_path(start, end):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        initial_pubs_sql ="""
            SELECT p.name, p.id, p.address, l.lat, l.lon
            FROM pub p, location l
            WHERE p.id = l.pub_id
            AND (l.lat BETWEEN %s AND %s)
            AND (l.lon BETWEEN %s AND %s)
            LIMIT 10"""

            """
            SELECT latitude, longitude, SQRT(
    POW(69.1 * (latitude - [startlat]), 2) +
    POW(69.1 * ([startlng] - longitude) * COS(latitude / 57.3), 2)) AS distance
FROM TableName HAVING distance < 25 ORDER BY distance;
            """

        next_pubs_sql = """

        """

        # find distance between start and end
        total_dist = int(get_distance(start[0], start[1], end[0], end[1]))
        print(total_dist)

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

        starting_pubs = cur.fetchall()
        for starting_pub in starting_pubs:
            print(starting_pub)
            next_pubs = plot_next(starting_pub, end)
            for next_pub in next_pubs:
                print(next_pub)


        # foreach starting point, plot the next point
        for starting_pub in starting_pubs:
            # find closest 5 pubs
            cur.execute(closest_pubs_sql, (starting_pub[1]))


        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    t1_start = process_time()

    # collect coordinates
    # start = input("starting coordinates (lat, long): ")
    start = "51.5007169,-0.1847102"
    start_lat, start_lon = start.split(',')
    try:
        start_lat = float(start_lat)
        start_lon = float(start_lon)
    except Exception as e:
        print(e)
        exit()
    # end = input("ending coordinates (lat, long): ")
    end = "51.4516815,-0.1827658"
    end_lat, end_lon = end.split(',')
    try:
        end_lat = float(end_lat)
        end_lon = float(end_lon)
    except Exception as e:
        print(e)
        exit()

    plot_path((start_lat, start_lon), (end_lat, end_lon))


    t1_stop = process_time()
    print("time taken: :", t1_stop-t1_start)


