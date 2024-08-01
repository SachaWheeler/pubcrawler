from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import Distance as D
from django.contrib.gis.db.models.functions import GeometryDistance
# from django.contrib.gis.db.models.functions import Distance
from .models import Pub
from .forms import CoordinateForm
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

class ShortestPathView(View):
    template_name = 'pubs/shortest_path.html'

    def get(self, request, *args, **kwargs):
        form = CoordinateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CoordinateForm(request.POST)
        if form.is_valid():
            start_lat = form.cleaned_data['start_lat']
            start_lon = form.cleaned_data['start_lon']
            end_lat = form.cleaned_data['end_lat']
            end_lon = form.cleaned_data['end_lon']

            # Convert to Point objects
            start_point = Point(start_lon, start_lat)  # Note the order: lon, lat
            end_point = Point(end_lon, end_lat)
            print(f"{start_point.x=}, {start_point.y=} - {end_point.x=}, {end_point.y=}")

            padding = 0.001
            min_lon = min(start_point.x, end_point.x) - padding
            max_lon = max(start_point.x, end_point.x) + padding
            min_lat = min(start_point.y, end_point.y) - padding
            max_lat = max(start_point.y, end_point.y) + padding

            bbox = (min_lon, min_lat, max_lon, max_lat)  #(xmin, ymin, xmax, ymax).
            geom = Polygon.from_bbox(bbox)
            print(bbox)


            print(f"{min_lat=}, {max_lat=}, {min_lon=}, {max_lon=}")

            # bounding box
            pubs = Pub.objects.filter(
                location__intersects=geom
            )

            print(f"{pubs}\n{len(pubs)=}")
            nearest_to_start = pubs.filter(
                location__distance_lte=(
                    start_point,
                    D(m=1000)
                )
            ).order_by(
                GeometryDistance("location", start_point)
            ).first()
            print(f"{nearest_to_start=}, {nearest_to_start.location}")

            nearest_to_end = pubs.filter(
                location__distance_lte=(
                    end_point,
                    D(m=1000)
                )
            ).order_by(
                GeometryDistance("location", end_point)
            ).first()
            print(f"{nearest_to_end=}")


            # Get the coordinates of the nearest point
            nearest_start_coords = (nearest_to_start.location.y, nearest_to_start.location.x)

            context = {
                'form': form,
                'route_image': '',
                'test': 'x'
            }

            # Return the rendered template with the image
            return render(request, self.template_name, context)

        # If form is not valid, re-render the form with errors
        return render(request, self.template_name, {'form': form})

