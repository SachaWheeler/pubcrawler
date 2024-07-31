from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.gis.geos import Point
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

            # Find the nearest location to the start_point
            """
            nearest_location = Pub.objects.annotate(
                distance=Distance('location', start_point)
            ).order_by('distance').first()
            """
            nearest_location = Pub.objects.filter(
                location__distance_lte=(
                    start_point,
                    D(m=1000)
                )
            ).order_by(
                GeometryDistance("location", start_point)
            ).first()

            if not nearest_location:
                return JsonResponse({"error": "No locations found in the database"}, status=404)

            # Get the coordinates of the nearest point
            nearest_start_coords = (nearest_location.location.y, nearest_location.location.x)

            # Use osmnx to download the map graph for the area surrounding the start and end points
            G = ox.graph_from_point(nearest_start_coords, dist=2000, network_type='walk')

            # Find the nearest nodes to the start and end points
            start_node = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
            end_node = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)

            # Calculate the shortest path
            route = nx.shortest_path(G, start_node, end_node, weight='length')

            # Plot the route
            fig, ax = ox.plot_graph_route(G, route, route_linewidth=6, node_size=0)

            # Save the plot to a BytesIO object and encode as base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

            # Return the rendered template with the image
            return render(request, self.template_name, {'form': form, 'route_image': img_base64})

        # If form is not valid, re-render the form with errors
        return render(request, self.template_name, {'form': form})

