#!/usr/bin/python
import csv
import psycopg2
from config import config
from time import process_time


def insert_pub(pub):
    """ insert a new pub into the pub table """
    name = pub[1]
    address = pub[2]
    postcode = pub[3]
    borough = pub[8]
    lat = pub[6]
    long = pub[7]
    try:
        float(lat)
        float(long)
    except Exception as e:
        return
    pub_sql = """INSERT INTO pub(name, address, postcode, borough)
             VALUES(%s, %s, %s, %s) RETURNING id;"""
    location_sql = """INSERT INTO location(pub_id, lat, long)
             VALUES(%s, %s, %s) RETURNING pub_id;"""
    conn = None
    vendor_id = None
    try:
        # read database configuration
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # save the pub details
        cur.execute(pub_sql, (name, address, postcode, borough))
        pub_id = cur.fetchone()[0]

        # save the location
        cur.execute(location_sql, (pub_id, lat, long))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return vendor_id

if __name__ == '__main__':
    t1_start = process_time()
    with open('data/open_pubs.csv', 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        count = 0
        for row in csv_reader:
            # INSERT INTO pub(name, address, postcode, borough)
            insert_pub(row)
            count += 1
            if count %500 == 0:
                print(f" {count}")
    t1_stop = process_time()
    print("time taken: :", t1_stop-t1_start)


