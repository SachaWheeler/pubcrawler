import osmnx as ox
import networkx as nx
from geopy.distance import geodesic, great_circle
from django.core.management.base import BaseCommand
from pubs.models import Pub, Distance
from django.db.models import Q
from os.path import exists


class Command(BaseCommand):
    help = 'Calculate distances between pubs'

    def handle(self, *args, **kwargs):
        # pubs = Pub.objects.filter(address__icontains="london") #.order_by('-pk')
        pubs = Pub.objects.filter(
                local_authority__name__in=["Westminster",
                    "Kensington and Chelsea",
                    "Islington",
                    "Hammersmith and Fulham",
                    # "Camden"
                    ]).order_by('pk')
        print(f"{len(pubs)=}")
        # return

        skipping = 0
        graph_file = "/home/sacha/work/pubcrawler/demo/maps/London.graphml";
        if exists(graph_file):
            print(f"Loading mapfile: {graph_file}")
            G = ox.load_graphml(graph_file)
            print("mapfile loaded")
        else:
            print(f"can't open {graph_file}")
            return

        for pub in pubs:
            pub_location = (pub.latitude, pub.longitude)

            delta = 0.02
            lat_min = pub.latitude  - delta
            lat_max = pub.latitude  + delta
            lon_min = pub.longitude - delta
            lon_max = pub.longitude + delta

            skip_pubs = [distance.pub2.id for distance in Distance.objects.filter(pub1=pub)]
            skip_pubs.extend([distance.pub1.id for distance in Distance.objects.filter(pub2=pub)])
            skip_pubs.extend([pub.id])  # exclude itself

            other_pubs = Pub.objects.filter(
                Q(latitude__lte=lat_max) &
                Q(latitude__gte=lat_min) &
                Q(longitude__lte=lon_max) &
                Q(longitude__gte=lon_min)
            ).exclude(id__in=set(skip_pubs))

            print(f"{pub}, {pub.address}, {len(other_pubs)}")
            count = 0
            writing = 0
            for other_pub in other_pubs:
                count += 1

                other_location = (other_pub.latitude, other_pub.longitude)
                # absolute_distance = geodesic(pub_location, other_location).meters # great_circle is faster
                absolute_distance = great_circle(pub_location, other_location).meters
                print(f"    {other_pub}, {absolute_distance:,.0f}m")

                if absolute_distance <= 2000:
                    # Calculate walking distance using osmnx
                    if not G:
                        print("no G")
                        G = ox.graph_from_point(pub_location, dist=1000, network_type='walk')
                    orig_node = ox.nearest_nodes(G, pub.longitude, pub.latitude)
                    dest_node = ox.nearest_nodes(G, other_pub.longitude, other_pub.latitude)
                    try:
                        walking_distance = nx.shortest_path_length(G, orig_node, dest_node, weight='length')
                    except nx.NetworkXNoPath:
                        walking_distance = None

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
            print(f"{count=}, {writing=}")

        self.stdout.write(self.style.SUCCESS('Successfully calculated and stored distances'))

