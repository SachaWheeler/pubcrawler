import osmnx as ox
import networkx as nx
from geopy.distance import geodesic, great_circle
from django.core.management.base import BaseCommand
from pubs.models import Pub, Distance
from django.db.models import Q
from os.path import exists
from django.contrib.gis.measure import Distance as D
from django.contrib.gis.db.models.functions import GeometryDistance
import time


class Command(BaseCommand):
    help = 'Calculate distances between pubs'

    def handle(self, *args, **kwargs):
        pubs = Pub.objects.all()
        """
        # Distance.objects.all().delete()
        # return

        pubs = Pub.objects.filter(
                local_authority__name__in=["Westminster",
                    "Kensington and Chelsea",
                    "Islington",
                    "Hammersmith and Fulham",
                    "Camden"
                    ])
        """

        print(f"{len(pubs)=}")
        # return

        skipping = 0
        #graph_file = "/home/sacha/work/pubcrawler/demo/maps/London_central.graphml"
        graph_file = "" #/home/sacha/work/pubcrawler/demo/maps/2_London.graphml"
        local_mapfile = False
        ox.settings.use_cache = True

        if exists(graph_file):
            print(f"Loading mapfile: {graph_file}")
            st = int(time.time())
            G = ox.load_graphml(graph_file)
            et = int(time.time())
            print(f'mapfile loaded: {et - st} seconds')
            local_mapfile = True

        DIST = 1000
        WALKING_DIST = 600
        MAX_NEAREST = 6

        for pub in pubs:
            pub_location = (pub.latitude, pub.longitude)

            other_pubs = Pub.objects.filter(
                location__distance_lte=(
                    pub.location,
                    D(m=DIST)
                )
            ).exclude(
                id=pub.id
            ).order_by(
                GeometryDistance("location", pub.location)
                )[:MAX_NEAREST]

            print(f"{pub}, {pub.address}, {len(other_pubs)}")
            if len(other_pubs) > 0 and not local_mapfile:
                G = ox.graph_from_point(pub_location, dist=DIST, network_type='walk')
            count = 0
            writing = 0
            for other_pub in other_pubs:
                count += 1

                if Distance.objects.filter(
                    Q(
                        Q(pub1=pub) & Q(pub2=other_pub)
                    ) | Q(
                        Q(pub1=other_pub) & Q(pub2=pub)
                    )
                ).exists():
                    continue
                other_location = (other_pub.latitude, other_pub.longitude)
                absolute_distance = great_circle(pub_location, other_location).meters
                print(f"    {other_pub}, {absolute_distance:,.0f}m")

                if 5 <= absolute_distance <= WALKING_DIST:
                    orig_node = ox.nearest_nodes(G, pub.longitude, pub.latitude)
                    dest_node = ox.nearest_nodes(G, other_pub.longitude, other_pub.latitude)
                    try:
                        walking_distance = nx.shortest_path_length(G, orig_node, dest_node,
                                weight='length')
                    except nx.NetworkXNoPath:
                        walking_distance = None

                    # break
                    if walking_distance:
                        writing += 1
                        absolute_distance = round(absolute_distance, 2)
                        walking_distance = round(walking_distance, 2)
                        Distance.objects.update_or_create(
                            pub1=pub,
                            pub2=other_pub,
                            defaults={
                                'absolute_distance': absolute_distance,
                                'walking_distance': walking_distance
                                }
                        )
                        if writing >= MAX_NEAREST:
                            break
            # break
            print(f"{count=}, {writing=}")

        self.stdout.write(self.style.SUCCESS('Successfully calculated and stored distances'))

