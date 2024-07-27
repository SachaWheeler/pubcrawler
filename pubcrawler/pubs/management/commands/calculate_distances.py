import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
from django.core.management.base import BaseCommand
from pubs.models import Pub, Distance

class Command(BaseCommand):
    help = 'Calculate distances between pubs'

    def handle(self, *args, **kwargs):
        pubs = Pub.objects.all()

        for pub in pubs:
            pub_location = (pub.latitude, pub.longitude)
            distances_to_others = []

            for other_pub in pubs:
                if pub != other_pub:
                    other_location = (other_pub.latitude, other_pub.longitude)
                    absolute_distance = geodesic(pub_location, other_location).meters

                    if absolute_distance <= 1000:
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
                Distance.objects.update_or_create(
                    pub1=pub1,
                    pub2=pub2,
                    defaults={
                        'absolute_distance': absolute_distance,
                        'walking_distance': walking_distance
                        }
                )

        self.stdout.write(self.style.SUCCESS('Successfully calculated and stored distances'))

