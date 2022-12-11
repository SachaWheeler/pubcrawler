#!/usr/bin/python
from configparser import ConfigParser


# http://bboxfinder.com/#51.418892,-0.248256,51.570653,-0.040889
LON_1, LAT_1, LON_2, LAT_2 = -0.248256,51.418892,-0.040889,51.570653

def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
