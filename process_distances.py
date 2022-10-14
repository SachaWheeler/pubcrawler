#!/usr/bin/python
import csv
import psycopg2
from config import config
from time import process_time
from math import sin, cos, sqrt, atan2, radians
import itertools

def get_distance(lat_a, lon_a, lat_b, lon_b):
    R = 6373.0 * 1000  # approximate radius of earth in metres

    lat1 = radians(lat_a)
    lon1 = radians(lon_a)
    lat2 = radians(lat_b)
    lon2 = radians(lon_b)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # in Km
    return distance


def process_distances():
    """ query data from the vendors table """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT pub_id, lat, long FROM location ORDER BY pub_id")
        locations = cur.fetchall()

        distance_sql = """INSERT INTO distance(start_loc, end_loc, distance)
            VALUES(%s, %s, %s);"""

        count = 0
        no = 0
        yes = 0
        for a, b in itertools.combinations(locations, 2):
            # (1, 51.970379, 0.97934) (2, 51.958698, 1.057832)
            count += 1
            distance = get_distance(a[1], a[2], b[1], b[2])
            if distance > 2000 or distance < 1:  # 2,000 metres
                no += 1
                continue
            # print(a, b, distance)
            cur.execute(distance_sql, (a[0], b[0], distance))

            yes += 1
            if x%1000 == 0:
                print(f"{count:,}, {no:,}, {yes:,}")

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

if __name__ == '__main__':
    t1_start = process_time()

    process_distances()

    t1_stop = process_time()
    print("time taken: :", t1_stop-t1_start)


