#!/usr/bin/python
import csv
import psycopg2
from config import config
from time import process_time
from math import sin, cos, sqrt, atan2, radians
import itertools

from process_distances import get_distance


def plot_path(start, end):
    """ query data from the vendors table """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # cur.execute("SELECT pub_id, lat, lon FROM location ORDER BY pub_id")

        # process
        print(start)
        print(end)

        # find distance between start and end
        total_dist = get_distance(start[0], start[1], end[0], end[1])
        print(total_dist)

        # find closest 5 pubs to start point in the right direction

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    t1_start = process_time()

    # collect coordinates
    start = input("starting coordinates (lat, long): ")
    start_lat, start_lon = start.split(',')
    try:
        start_lat = float(start_lat)
        start_lon = float(start_lon)
    except Exception as e:
        print(e)
        exit()
    end = input("ending coordinates (lat, long): ")
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


