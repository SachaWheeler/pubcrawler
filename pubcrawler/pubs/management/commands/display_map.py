import osmnx as ox
import networkx as nx
from geopy.distance import geodesic, great_circle
from django.core.management.base import BaseCommand
from pubs.models import Pub, PubDist
from django.db.models import Q
from os.path import exists
import matplotlib.pyplot as plt

import time


class Command(BaseCommand):
    help = 'Calculate distances between pubs'

    def handle(self, *args, **kwargs):

        graph_file = "/home/sacha/work/pubcrawler/demo/maps/2_London.graphml"
        # graph_file = "/home/sacha/work/pubcrawler/demo/maps/London_central.graphml"

        if exists(graph_file):
            print(f"Loading mapfile: {graph_file}")
            st = int(time.time())
            G = ox.load_graphml(graph_file)
            et = int(time.time())
            print(f'mapfile loaded: {et - st} seconds')
        else:
            print(f"can't open {graph_file}")
            return

        print("plotting")
        fig, ax = ox.plot_graph(G)
        print("showing")
        plt.show()
