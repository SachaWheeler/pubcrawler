from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Pub  # Replace with your actual model name


def find_closest_point(pubs_within_bbox, start_point):
    # Find the closest point in the DB to the start_point
    closest_point = pubs_within_bbox.annotate(
        distance=Distance('geo_location', start_point)
    ).order_by('distance').first()

    return closest_point

def find_paths(pubs_within_bbox, start_point, end_point):
    # Find the closest point in the DB to the start_point
    closest_point = find_closest_point(pubs_within_bbox, start_point)

    if closest_point is None:
        return []

    path = [closest_point.geo_location]
    current_point = closest_point.geo_location

    while True:
        # Find the nearest point in the DB that gets closer to the end_point and hasn't been visited yet
        print(F"{path=}, {current_point=}")
        next_points = pubs_within_bbox.exclude(geo_location__in=path).annotate(
            distance=Distance('geo_location', current_point),
            to_end=Distance('geo_location', end_point)
        ).filter(to_end__lt=Distance('geo_location', current_point)).order_by('distance')

        if not next_points.exists():
            break  # No more points that get closer to the end_point

        next_point = next_points.first().geo_location

        path.append(next_point)
        current_point = next_point

        # Stop if the next point is very close to the end_point
        if current_point.distance(end_point) < 0.003:  # Distance threshold, e.g., 1 meter
            break

    return path

