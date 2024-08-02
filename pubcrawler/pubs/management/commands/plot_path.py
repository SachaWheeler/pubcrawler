from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, Polygon, GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from pubs.models import Pub, PubDist
from django.db.models import Q
from pubs.utils import find_closest_points, find_paths


class Command(BaseCommand):
    help = 'Shortest path between pubs'

    def handle(self, *args, **kwargs):


        SACHA           = (51.5007169,-0.1847102)
        BROMPTON        = (51.4840451,-0.1919901)
        SPORTING_PAGE   = (51.4848277,-0.1830941)
        LIZZIE          = (51.5447774,-0.1184278)
        LOTTIE          = (51.5359589,-0.2059297)
        EXMOUTH         = (51.5258245,-0.111508)
        SOHO            = (51.5111286,-0.139059)

        start, end = SACHA, SOHO

        start_lat, start_lon, end_lat, end_lon = start[0], start[1], end[0], end[1]

        # start_point = Point(start_lon, start_lat)
        start_point = GEOSGeometry(f'POINT({start_lon} {start_lat})', srid=4326)
        start_point_proj = start_point.transform(32631, clone=True)

        # end_point = Point(end_lon, end_lat)
        end_point = GEOSGeometry(f'POINT({end_lon} {end_lat})', srid=4326)
        end_point_proj = end_point.transform(32631, clone=True)

        total_journey_distance = int(start_point_proj.distance(end_point_proj))
        print(f"{total_journey_distance=}")

        # Step 1: Filter points within the bounding box
        delta = 0.01
        min_lat = min(start_lat, end_lat) - delta
        max_lat = max(start_lat, end_lat) + delta
        min_lon = min(start_lon, end_lon) - delta
        max_lon = max(start_lon, end_lon) + delta

        bounding_box = Polygon.from_bbox((min_lon, min_lat, max_lon, max_lat))
        pubs_within_bbox = Pub.objects.filter(geo_location__intersects=bounding_box)
        pub_point = dict([(pub.geo_location, f"{pub.name}, {pub.address}") for pub in pubs_within_bbox])
        # print(pub_point)

        # print(pubs_within_bbox, f"{len(pubs_within_bbox)=}")
        # print()
        # return

        current_point = start_point
        remaining_distance = total_journey_distance

        # Find the paths
        # path = find_paths(pubs_within_bbox, start_point, end_point)
        shortest_paths = find_paths(
                pubs_within_bbox,
                start_point, end_point,
                max_paths=3)

        print(shortest_paths)
        # Display the paths
        for idx, (total_distance, path) in enumerate(shortest_paths):
            # print(f"Path {idx + 1}:")
            for point, dist in path:
                print(f"  {pub_point[point]}, {dist.m:,.0f} meters")
            print(f"  Total Path Distance: {total_distance.m:,.0f} meters\n")

        """
        for point in path:
            print(pub_point[point])
        """




