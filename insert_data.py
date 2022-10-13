#!/usr/bin/python

import psycopg2
from config import config


def insert_pub(pub):
    """ insert a new pub into the pub table """
    name = pub['name']
    address = pub['address']
    postcode = pub['postcode']
    borough = pub['borough']
    sql = """INSERT INTO pub(name, address, postcode, borough)
             VALUES(%s) RETURNING id;"""
    conn = None
    vendor_id = None
    try:
        # read database configuration
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(sql, (name, address, postcode, borough))
        # get the generated id back
        pub_id = cur.fetchone()[0]
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
    # insert one vendor
    insert_vendor("3M Co.")
