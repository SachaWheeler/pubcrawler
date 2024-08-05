from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from .models import Pub, PubDist
from heapq import heappush, heappop
from types import SimpleNamespace
from functools import lru_cache


@lru_cache(maxsize=None)
def convert_to_geometry(point=None):
    if point is None:
        return
    # print(point) print(point.x) print(point.y)
    temp_point = GEOSGeometry(f'POINT({point.x} {point.y})', srid=4326)
    return temp_point.transform(32631, clone=True)

@lru_cache(maxsize=None)
def find_closest_points(pubs_within_bbox, current_point, end_point, n=3):
    # Find the `n` closest points to current_point that are closer to end_point
    if Pub.objects.filter(geo_location=current_point).exists():
        # print("point in DB")
        end_point_proj = convert_to_geometry(end_point)

        current_pub = Pub.objects.filter(geo_location=current_point).first()
        current_pub_proj = convert_to_geometry(current_pub.geo_location)

        closest_pubs = [(dist.pub1, dist.walking_distance) for dist in PubDist.objects.filter(pub2=current_pub)]
        closest_pubs.extend([(dist.pub2, dist.walking_distance) for dist in PubDist.objects.filter(pub1=current_pub)])

        sorted_closest_pubs = sorted(closest_pubs, key=lambda x: x[-1])[:n]

        closest_points = []

        for pub in sorted_closest_pubs:
            # print(f"{pub[1]=}")
            next_pub_proj = convert_to_geometry(pub[0].geo_location)
            if abs(next_pub_proj.distance(end_point_proj)) < abs(current_pub_proj.distance(end_point_proj)):
                print(current_pub, ' - ',  pub[0])
                pub_obj = SimpleNamespace(
                    name=pub[0].name,
                    address=pub[0].address,
                    geo_location=pub[0].geo_location,
                    distance=D(pub[1])
                )
                closest_points.append(pub_obj)

    else:
        # print("point not in DB")
        closest_points = pubs_within_bbox.annotate(
            distance=Distance('geo_location', current_point),
            to_end=Distance('geo_location', end_point)
        ).filter(
            to_end__lt=Distance(current_point, end_point)  # Only include points closer to the end_point
        ).order_by('distance')[:n]

    return list(closest_points)

def find_paths(pubs_within_bbox, start_point, end_point, max_paths=4):
    # Priority queue to store paths (by total distance)
    priority_queue = []
    initial_closest_points = find_closest_points(pubs_within_bbox, start_point, end_point, n=3)
    print(f"{initial_closest_points=}")

    # Initialize the queue with paths starting from the 3 closest points to the start_point
    for loc in initial_closest_points:
        path = [(loc.geo_location, loc.distance)]
        heappush(priority_queue, (loc.distance, path))

    completed_paths = []

    while priority_queue and len(completed_paths) < max_paths:
        # Get the shortest path in the priority queue
        total_distance, path = heappop(priority_queue)
        current_point = path[-1][0]

        if current_point.distance(end_point) < 0.0026:  # Close enough to the end point
            completed_paths.append((total_distance, path))
            continue

        # Find the 3 closest points to the current point, excluding already visited points
        next_closest_points = find_closest_points(pubs_within_bbox, current_point, end_point, n=3)

        for loc in next_closest_points:
            if loc.geo_location in [p[0] for p in path]:
                continue  # Skip already visited points

            # Create a new path by extending the current path
            new_path = path + [(loc.geo_location, loc.distance)]
            new_total_distance = total_distance + loc.distance

            # Add the new path to the priority queue
            heappush(priority_queue, (new_total_distance, new_path))

    return completed_paths
