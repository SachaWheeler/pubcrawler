import osmnx as ox
import networkx as nx
from geopy.distance import geodesic, great_circle
from django.core.management.base import BaseCommand
from pubs.models import Pub, PubDist
from django.db.models import Q
from os.path import exists
import time
from django.contrib.gis.geos import Point, GEOSGeometry


class Command(BaseCommand):
    help = 'turn lat lon into Points'

    def handle(self, *args, **kwargs):

        pubs = Pub.objects.all()
        print(f"{len(pubs)=}")
        # return
        count = 0
        for pub in pubs:
            count += 1

            #print(pub, pub.location, pub.geo_location)
            if pub.location:
                # Convert geography Point to a GEOSGeometry (which is a Geometry type)
                pub.geo_location = GEOSGeometry(pub.location)
                pub.save()
                # print(pub, pub.location, pub.geo_location)
                # break

            # break
            if count%100==0:
                print(f"{count=}")
