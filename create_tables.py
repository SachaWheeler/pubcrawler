#!/usr/bin/python

import psycopg2
from config import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE pub (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            address VARCHAR(255) NOT NULL,
            postcode VARCHAR(10) NOT NULL,
            local VARCHAR(20) NOT NULL
        )
        """,
        """ CREATE TABLE lat_long (
                pub_id SERIAL PRIMARY KEY,
                lat float,
                long float,
                CONSTRAINT fk_lat_long_pub
                    FOREIGN KEY(pub_id)
                    REFERENCES pub(id)
                )
        """
    )
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
