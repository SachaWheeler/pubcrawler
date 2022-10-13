#!/usr/bin/python

import psycopg2
from config import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        " DROP TABLE IF EXISTS pub CASCADE",
        " DROP TABLE IF EXISTS location CASCADE",
        " DROP TABLE IF EXISTS distance CASCADE",

        """
        CREATE TABLE pub (
            id SERIAL PRIMARY KEY,
            name VARCHAR(60) NOT NULL,
            address VARCHAR(100) NOT NULL,
            postcode VARCHAR(10) NOT NULL,
            borough VARCHAR(30) NOT NULL
        )
        """,
        """
        CREATE TABLE location (
            pub_id SERIAL PRIMARY KEY,
            lat float,
            long float,
            CONSTRAINT fk_location_pub
                FOREIGN KEY(pub_id)
                REFERENCES pub(id)
            )
        """,
        """
        CREATE TABLE distance (
            id SERIAL PRIMARY KEY,
            start_loc integer,
            end_loc integer,
            CONSTRAINT fk_start_loc
                FOREIGN KEY(start_loc)
                REFERENCES location(pub_id)
                ON DELETE CASCADE,
            CONSTRAINT fk_end_loc
                FOREIGN KEY(end_loc)
                REFERENCES location(pub_id)
                ON DELETE CASCADE
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
