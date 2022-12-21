#!/usr/bin/python
import csv
import pprint
import psycopg2
from config import config
from time import process_time
from math import sin, cos, sqrt, atan2, radians
import itertools
import difflib
import re

from process_distances import get_distance
from process_walking_distances import load_map

from anytree import Node, RenderTree, PreOrderIter, NodeMixin


MAX_RECURSION_LEVEL = 30
MAX_CHILD_COUNT = 1
MIN_DIST = 500
MAX_DIST = 2000

SACHA           = "51.5007169,-0.1847102"
BROMPTON        = "51.4840451,-0.1919901"
SPORTING_PAGE   = "51.4848277,-0.1830941"
LIZZIE          = "51.5447774,-0.1184278"
LOTTIE          = "51.5359589,-0.2059297"

START = LIZZIE
END = LOTTIE

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
                 lat=None, lon=None, walking_distance=None):
        self.id = id
        self.name = name
        self.address = address.replace("LONDON", "").replace("PUBLIC HOUSE, ", "").replace("PUBLIC HOUSE", "").replace("Public House, ", "").replace("Public House", "").replace(" ,", "")
        self.lat = lat
        self.lon = lon
        self.walking_distance = walking_distance

    def __str__(self):
        return f"{self.name}, {self.address}"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


def tuple_to_pub(pub_tuple=None):
    if pub_tuple is None:
        return None
    (name, id, address, lat, lon, walking_distance) = pub_tuple
    return Pub(
        id = id,
        name = name,
        address = address,
        lat = lat,
        lon = lon,
        walking_distance = walking_distance
    )

KM_TO_DEGREES = 0.00904 / 2
initial_pubs_sql ="""
    SELECT p.name, p.id, p.address, l.lat, l.lon
    FROM pub p, location l
    WHERE p.id = l.pub_id
    AND (l.lat BETWEEN %s AND %s)
    AND (l.lon BETWEEN %s AND %s)
    LIMIT 6
    """

ORDER = ""  # "DESC"
next_pubs_sql =f"""
select * from (
    SELECT p.name, p.id, p.address, l.lat, l.lon, d.walking_distance
    FROM pub p, location l, distance d

    WHERE p.id = d.end_loc
        AND l.pub_id = d.end_loc
        AND d.start_loc = %s
        AND d.walking_distance BETWEEN {MIN_DIST} AND {MAX_DIST}

    UNION ALL

    SELECT p.name, p.id, p.address, l.lat, l.lon, d.walking_distance
    FROM pub p, location l, distance d
    WHERE p.id = d.start_loc
        AND l.pub_id = d.start_loc
        AND d.end_loc = %s
        AND d.walking_distance BETWEEN {MIN_DIST} AND {MAX_DIST}
) t order by 6 {ORDER}

    """

def starting_points(start, end):  # (start_lat, start_lon), (end_lat, end_lon))
    paths = []
    # find bounding box for first pub - 1000m
    # print("starting points:", start, end)
    if start[0] < end[0]:  # going north
        # print("north")
        south_bound = start[0] - KM_TO_DEGREES
        north_bound = start[0] + KM_TO_DEGREES
    else:  # going south
        # print("south")
        south_bound = start[0] - KM_TO_DEGREES
        north_bound = start[0] + KM_TO_DEGREES

    if start[1] < end[1]:  # going west
        # print("west")
        east_bound = start[1] + KM_TO_DEGREES
        west_bound = start[1] - KM_TO_DEGREES
    else:  # going east
        # print("east")
        east_bound = start[1] + KM_TO_DEGREES
        west_bound = start[1] - KM_TO_DEGREES
    # print(f"east bound: {east_bound}")
    # print(f"west bound: {west_bound}")
    # print(f"south bound: {south_bound}")
    # print(f"north bound: {north_bound}")
    # print(f"north east: {north_bound}, {east_bound}")
    # print(f"north west: {north_bound}, {west_bound}")
    # print(f"south west: {south_bound}, {west_bound}")
    # print(f"south east: {south_bound}, {east_bound}")
    # exit(0)

    # find closest 5 pubs to start point in the right direction
    """
    cur.execute(initial_pubs_sql % (
        "{:.6f}".format(south_bound),
        "{:.6f}".format(north_bound),
        "{:.6f}".format(east_bound),
        "{:.6f}".format(west_bound)))
    """
    cur.execute(initial_pubs_sql,
                (south_bound, north_bound,
                 west_bound, east_bound))

    start_pubs = cur.fetchall()
    # pprint.pprint(start_pubs)
    """
    ('Doyles Tavern',
    11038,
    'Doyles Tavern, 379 Caledonian Road, Islington, London',
    51.543425, -0.11775),

    """

    for pub in start_pubs:
        distance = int(get_distance(start[0], start[1], pub[3], pub[4]))
        paths.append(pub + (distance,))
    paths.sort(key=lambda array_tup: array_tup[0][5])  # sorts in place
    # print([tuple_to_pub(pub) for pub in paths])
    return [tuple_to_pub(pub) for pub in paths]

def plot_next_steps(this, end):  # ((pub object), (end_lat, end_lon))
    # find closest pubs
    # pprint.pprint(f"tyhis {this} {this.pub}")
    pub = this.pub
    cur.execute(next_pubs_sql % (pub.id, pub.id))
    next_pubs = cur.fetchall()

    current_distance = get_distance(pub.lat, pub.lon, end[0], end[1])
    next_count = 0
    next_steps = []
    for sub_idx, next_pub in enumerate(next_pubs):
        pub_obj = tuple_to_pub(next_pub)
        pub_distance_to_target = get_distance(
            pub_obj.lat, pub_obj.lon,
            end[0], end[1]
        )
        if current_distance - pub_distance_to_target <= 0: # if further away from target
            continue
        next_count += 1
        next_steps.append(pub_obj)
        if next_count == MAX_CHILD_COUNT:
            break

    return next_steps


if __name__ == '__main__':
    t1_start = process_time()

    # collect coordinates
    start = input("starting coordinates (lat, long): ")
    if "," not in start:
        start = START
        print(f"start: {START}")
    start_lat, start_lon = start.split(',')
    try:
        start_lat = float(start_lat)
        start_lon = float(start_lon)
    except Exception as e:
        print(e)
        exit()
    end = input("ending coordinates (lat, long): ")
    if "," not in end:
        end = END
        print(f"end: {END}")
    end_lat, end_lon = end.split(',')
    try:
        end_lat = float(end_lat)
        end_lon = float(end_lon)
    except Exception as e:
        print(e)
        exit()

    # find distance between start and end
    total_dist = int(get_distance(start_lat, start_lon, end_lat, end_lon))
    print(f"({start_lat}, {start_lon}), ({end_lat}, {end_lon})")
    print(f"total distance: {total_dist:,}m")

    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        pubcrawl = Node(f"({start_lat}, {start_lon}), ({end_lat}, {end_lon})")

        print("started")
        #  WNode(pub, parent=a, weight=2)
        for pub in starting_points((start_lat, start_lon), (end_lat, end_lon)):
            # calculate distance
            dist = get_distance(start_lat, start_lon, pub.lat, pub.lon)
            node = WNode(pub, parent=pubcrawl, weight=int(dist))

        for pub_node in PreOrderIter(pubcrawl, maxlevel=MAX_RECURSION_LEVEL):
            if isinstance(pub_node, Node):
                # print(f"skipping {pub_node}")
                continue

            for next_pub in plot_next_steps( pub_node, (end_lat, end_lon)):
                WNode(next_pub, parent=pub_node, weight=next_pub.walking_distance)
        print("routes done")

        """ """
        # render to screen
        for pre, fill, node in RenderTree(pubcrawl):
            if isinstance(node, Node):
                print("%s%s" % (pre, node))
            else:
                print("%s%s (%sm)" % (pre, node, node.weight))
        """ """

        # find all paths from leaf nodes to root
        leaves = list(PreOrderIter(pubcrawl, filter_=lambda node: node.is_leaf))
        print("leaves done")
        paths = []
        for leaf in leaves:
            # print(leaf, leaf.pub.id)
            steps = []
            for p in leaf.path:
                if isinstance(p, Node):
                    # print(p)
                    continue
                else:
                    steps.append(p.pub.id)
            paths.append(steps)
        # pprint.pprint(paths)
        print(f"{len(paths)} paths")

        score_similar = 0
        score_different = 100
        similar = None
        different = None
        for a, b in itertools.combinations(paths, 2):
            seq = difflib.SequenceMatcher(None, a, b)
            ratio = seq.ratio()
            # print(ratio)
            if ratio > score_similar:
                score_similar = ratio
                similar = (a, b)
            if ratio < score_different:
                score_different = ratio
                different = (a, b)
        # print(f"similar {score_similar} ")
        # pprint.pprint(similar)
        # print("\n")
        print(f"different {score_different}")
        pprint.pprint(different)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    t1_stop = process_time()
    print("time taken: :", t1_stop-t1_start)


