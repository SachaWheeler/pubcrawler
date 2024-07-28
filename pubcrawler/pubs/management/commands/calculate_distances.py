import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
from django.core.management.base import BaseCommand
from pubs.models import Pub, Distance
from django.db.models import Q


class Command(BaseCommand):
    help = 'Calculate distances between pubs'

    def handle(self, *args, **kwargs):
        """
        # london-ish
        51.6225941,-0.4041025
        51.3876345,0.0742792
        """
        # pubs = Pub.objects.filter(address__icontains="london") #.order_by('-pk')
        pubs = Pub.objects.filter(
                local_authority__name__in=[# "Westminster",
                    "Kensington and Chelsea",
                    # "Hammersmith and Fulham",
                    # "Camden"
                    ]).order_by('latitude', 'longitude')
                # Q(latitude__lte=51.6225941) &
                # Q(latitude__gt=51.3876345) &
                # Q(longitude__lte=0.0742792) &
                # Q(longitude__gt=-0.4041025))  #.order_by('-pk')
        print(f"{len(pubs)=}")
        # return

        count = 0
        skipping = 0
        writing = 0
        for pub in pubs:
            pub_location = (pub.latitude, pub.longitude)
            distances_to_others = []

            for other_pub in pubs:
                count += 1
                print(f"{count=}, {skipping=}, {writing=}")

                """
                """
                if Distance.objects.filter(Q(pub1=pub, pub2=other_pub) | Q(pub2=pub, pub1=other_pub)).exists():
                    skipping += 1
                    continue
                """
                """

                if pub != other_pub:
                    other_location = (other_pub.latitude, other_pub.longitude)
                    absolute_distance = geodesic(pub_location, other_location).meters

                    if absolute_distance <= 2000:
                        # Calculate walking distance using osmnx
                        G = ox.graph_from_point(pub_location, dist=1000, network_type='walk')
                        orig_node = ox.nearest_nodes(G, pub.longitude, pub.latitude)
                        dest_node = ox.nearest_nodes(G, other_pub.longitude, other_pub.latitude)
                        try:
                            walking_distance = nx.shortest_path_length(G, orig_node, dest_node, weight='length')
                        except nx.NetworkXNoPath:
                            walking_distance = None

                        if walking_distance:
                            distances_to_others.append((pub, other_pub, absolute_distance, walking_distance))

            for pub1, pub2, absolute_distance, walking_distance in distances_to_others:
                writing += 1
                absolute_distance = round(absolute_distance, 2)
                walking_distance = round(walking_distance, 2)
                Distance.objects.update_or_create(
                    pub1=pub1,
                    pub2=pub2,
                    defaults={
                        'absolute_distance': absolute_distance,
                        'walking_distance': walking_distance
                        }
                )

        self.stdout.write(self.style.SUCCESS('Successfully calculated and stored distances'))

