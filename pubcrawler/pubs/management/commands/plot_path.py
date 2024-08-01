from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, Polygon, GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance as DD
from pubs.models import Pub, PubDist



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

        start_lat, start_lon, end_lat, end_lon = SACHA[0], SACHA[1], SPORTING_PAGE[0], SPORTING_PAGE[1]

        # start_point = Point(start_lon, start_lat)
        start_point = GEOSGeometry(f'POINT({start_lon} {start_lat})', srid=4326)

        # end_point = Point(end_lon, end_lat)
        end_point = GEOSGeometry(f'POINT({end_lon} {end_lat})', srid=4326)

        # Step 1: Filter points within the bounding box
        delta = 0.01
        min_lat = min(start_lat, end_lat) - delta
        max_lat = max(start_lat, end_lat) + delta
        min_lon = min(start_lon, end_lon) - delta
        max_lon = max(start_lon, end_lon) + delta

        bounding_box = Polygon.from_bbox((min_lon, min_lat, max_lon, max_lat))
        points_within_bbox = Pub.objects.filter(geo_location__intersects=bounding_box)

        print(points_within_bbox, len(points_within_bbox))
        # return

        current_point = start_point
        path = [start_point]

        while True:
            # Exclude the current point from the search
            """
            # Use PubDist table instead
            nearest_points = points_within_bbox.annotate(
                distance=DD('location', current_point),
                to_end=DD('location', end_point)
            ).filter(to_end__lt=DD('location', current_point)).order_by('distance')
            """

            # Find the Nearest Pub to the current_point
            nearest_points = points_within_bbox.annotate(
                    distance=DD("geo_location", current_point)
                    ).order_by('distance')
            print(f"{current_point=}, {nearest_points}")
            break

            # repeat

            if not nearest_points.exists():
                break  # No more points that get closer to the end point

            nearest_point = nearest_points.first().geo_location

            # Avoid going back to the same point
            if nearest_point in path:
                break

            path.append(nearest_point)
            current_point = nearest_point

            # Check if the nearest point is very close to the end point
            if current_point.distance(end_point) < 0.001:  # Distance threshold, e.g., 1 meter
                break

        path.append(end_point)
        return path
