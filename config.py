#!/usr/bin/python
from configparser import ConfigParser
from anytree import NodeMixin


# https://tripadvisor-content-api.readme.io/reference/overview
TRIPADVISOR_API_KEY = "CA5AE29CCF0240FBAC51AA592C55EFEE"

# http://bboxfinder.com/#51.418892,-0.248256,51.570653,-0.040889
# LON_1, LAT_1, LON_2, LAT_2 = -0.230977,51.487018,-0.092103,51.551963
LON_1, LAT_1, LON_2, LAT_2 = -0.248256,51.418892,-0.040889,51.570653  # larger
if LON_1 < LON_2:
    EAST = LON_1
    WEST = LON_2
else:
    EAST = LON_2
    WEST = LON_1
if LAT_1 < LAT_2:
    NORTH = LAT_2
    SOUTH = LAT_1
else:
    NORTH = LAT_1
    SOUTH = LAT_2


MAP_NAME = "London_central"

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


class WNode(NodeMixin):
    def __init__(self, pub, parent=None, weight=None):
        super(WNode, self).__init__()
        self.pub = pub
        self.parent = parent
        self.weight = weight if parent is not None else None

    def _post_detach(self, parent):
        self.weight = None

    def __str__(self):
        return str(self.pub)


class Pub:
    def __init__(self, id=None, name=None, address=None,
                 lat=None, lon=None, walking_distance=None,
                 rating=None, hygiene=None, confidence=None, structure=None):
        self.id = id
        self.name = name
        # self.address = address.replace("LONDON", "").replace("PUBLIC HOUSE, ", "").replace("PUBLIC HOUSE", "").replace("Public House, ", "").replace("Public House", "").replace(" ,", "")
        self.address = address
        self.lat = lat
        self.lon = lon
        self.walking_distance = walking_distance
        self.rating = rating
        self.hygiene = hygiene
        self.confidence = confidence
        self.structure = structure

    def __str__(self):
        return f"{self.name}, {self.address} ({self.rating}, {self.hygiene}, {self.confidence}, {self.structure})"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


def tuple_to_pub(pub_tuple=None):
    if pub_tuple is None:
        return None
    (name, id, address, lat, lon, walking_distance, rating, hygiene, confidence, structure, _) = pub_tuple
    return Pub(
        id = id,
        name = name,
        address = address,
        lat = lat,
        lon = lon,
        walking_distance = walking_distance,
        rating = rating,
        hygiene = hygiene,
        confidence = confidence,
        structure = structure
    )

def get_walking_distance(cur, pub_a, pub_b):
    get_walking_distance_sql = f"""
    SELECT walking_distance
    FROM distance d
    WHERE (start_loc = {pub_a} AND end_loc = {pub_b})
    OR (start_loc = {pub_b} AND end_loc = {pub_a})
    """
    cur.execute(get_walking_distance_sql)
    walking_distance = cur.fetchone()
    return walking_distance[0]

def get_pub(cur, pub_id):

    get_pub_sql =f"""
    SELECT p.name, p.id, p.address, l.lat, l.lon,
        p.rating, p.hygiene, p.confidence, p.structural,
        COALESCE(p.hygiene, 2) + COALESCE(p.confidence, 2) + COALESCE(p.structural, 0) as score
    FROM pub p, location l
    WHERE p.id = %s
    AND l.pub_id = p.id
    """
    cur.execute(get_pub_sql, (pub_id,))
    pub = cur.fetchone()
    return pub

KM_TO_DEGREES = 0.00904 / 2
