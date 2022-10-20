#!/usr/bin/python

import psycopg2
from config import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        # " DROP TABLE IF EXISTS borough CASCADE",
        # " DROP TABLE IF EXISTS pub CASCADE",
        # " DROP TABLE IF EXISTS location CASCADE",
        # " DROP TABLE IF EXISTS distance CASCADE",

        """
        CREATE TABLE IF NOT EXISTS borough (
            id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL,
            UNIQUE(name)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS pub (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            address VARCHAR(150) NOT NULL,
            postcode VARCHAR(10) NOT NULL,
            borough integer NOT NULL,
            CONSTRAINT fk_borough_id
                FOREIGN KEY(borough)
                REFERENCES borough(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS location (
            pub_id SERIAL PRIMARY KEY,
            lat float NOT NULL,
            lon float NOT NULL,
            CONSTRAINT fk_location_pub
                FOREIGN KEY(pub_id)
                REFERENCES pub(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS distance (
            id SERIAL PRIMARY KEY,
            start_loc integer NOT NULL,
            end_loc integer NOT NULL,
            distance integer NOT NULL,
            CONSTRAINT fk_start_loc
                FOREIGN KEY(start_loc)
                REFERENCES location(pub_id)
                ON DELETE CASCADE,
            CONSTRAINT fk_end_loc
                FOREIGN KEY(end_loc)
                REFERENCES location(pub_id)
                ON DELETE CASCADE,
            UNIQUE (start_loc, end_loc)
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
