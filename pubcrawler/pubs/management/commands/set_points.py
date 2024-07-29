import osmnx as ox
import networkx as nx
from geopy.distance import geodesic, great_circle
from django.core.management.base import BaseCommand
from pubs.models import Pub, Distance
from django.db.models import Q
from os.path import exists
import time
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = 'turn lat lon into Points'

    def handle(self, *args, **kwargs):

        pubs = Pub.objects.all()
        print(f"{len(pubs)=}")
        count = 0
        for pub in pubs:
            count += 1
            pub.location = Point(pub.longitude, pub.latitude)
            pub.save()
            # break
            if count%100==0:
                print(f"{count=}")
