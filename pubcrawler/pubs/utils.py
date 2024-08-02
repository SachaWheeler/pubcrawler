from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Pub  # Replace with your actual model name
from heapq import heappush, heappop

def find_closest_points(pubs_within_bbox, current_point, end_point, n=3):
    # Find the `n` closest points to current_point that are closer to end_point
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
    print(initial_closest_points)

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
